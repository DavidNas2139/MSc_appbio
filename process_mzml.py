#!/usr/bin/env python3
import os 
import sys  # Added for error handling
import json
import pyopenms as oms 
import pandas as pd 
import xml.etree.ElementTree as ET
import numpy as np
from tqdm import tqdm
import argparse

def load_params(config_path="params.json"):
    """Load parameters from JSON file."""
    with open(config_path) as f:
        return json.load(f)
def decode_mzml_id(encoded_id):
    """Decodes mzML-specific encoding like _x0020_ to spaces"""
    if not encoded_id:
        return encoded_id
    parts = []
    current_pos = 0
    while True:
        start = encoded_id.find('_x', current_pos)
        if start == -1:
            parts.append(encoded_id[current_pos:])
            break
        hex_part = encoded_id[start+2:start+6]
        if len(hex_part) == 4 and all(c in '0123456789ABCDEFabcdef' for c in hex_part):
            parts.append(encoded_id[current_pos:start])
            char_code = int(hex_part, 16)
            parts.append(chr(char_code))
            current_pos = start + 6
        else:
            parts.append(encoded_id[current_pos:start+2])
            current_pos = start + 2
    return ''.join(parts)

def get_sample_id(mzml_file):
    """Extracts sample ID from mzML metadata"""
    try:
        tree = ET.parse(mzml_file)
        root = tree.getroot()
        ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {'ns': ''}
        sample = root.find('.//ns:sample', ns) or root.find('.//sample')
        return decode_mzml_id(sample.get('id')) if sample is not None else None
    except Exception as e:
        print(f"Error parsing {mzml_file}: {str(e)}", file=sys.stderr)
        return None

def bin_features(feature_map, mz_bin_size=0.005, rt_bin_size=5.0):
    """High-res optimized binning with numpy/pandas."""
    # Convert to arrays
    mz = np.array([f.getMZ() for f in feature_map])
    rt = np.array([f.getRT() for f in feature_map])
    intensity = np.array([f.getIntensity() for f in feature_map])
    charge = np.array([f.getCharge() for f in feature_map])

    # Bin calculation (vectorized)
    mz_bins = np.round(mz / mz_bin_size) * mz_bin_size
    rt_bins = np.round(rt / rt_bin_size) * rt_bin_size

    # Pandas aggregation
    df = pd.DataFrame({
        'mz_bin': mz_bins, 
        'rt_bin': rt_bins,
        'intensity': intensity,
        'charge': charge
    })
    binned = df.groupby(['mz_bin', 'rt_bin']).agg({
        'intensity': 'sum',
        'charge': lambda x: x.mode()[0] if not x.empty else 0
    }).reset_index()

    # Rebuild FeatureMap
    binned_fm = oms.FeatureMap()
    for _, row in binned.iterrows():
        feat = oms.Feature()
        feat.setMZ(row['mz_bin'])
        feat.setRT(row['rt_bin'])
        feat.setIntensity(row['intensity'])
        feat.setCharge(int(row['charge']))
        binned_fm.push_back(feat)
    
    return binned_fm

def process_mzML(mzML_path, params):
    """Process mzML file with high-res settings."""
    try:
        # Get Sample Id
        sample_id = get_sample_id(mzML_path) or os.path.splitext(os.path.basename(mzML_path))[0] 

        # 1. Load data
        exp = oms.MSExperiment()
        oms.MzMLFile().load(mzML_path, exp)
        exp.sortSpectra(True)

        # 2. Detect mass traces
        mass_traces = []
        mtd = oms.MassTraceDetection()
        mtd_params = mtd.getDefaults()
        mtd_params.setValue("mass_error_ppm", params['mass_error_ppm'])
        mtd_params.setValue("noise_threshold_int", params['min_intensity'])
        mtd.setParameters(mtd_params)
        mtd.run(exp, mass_traces, 0)

        # 3. Detect elution peaks
        mass_traces_split = []
        epd = oms.ElutionPeakDetection()
        epd_params = epd.getDefaults()
        epd_params.setValue("width_filtering", "auto")
        epd.setParameters(epd_params)
        epd.detectPeaks(mass_traces, mass_traces_split)

        # 4. Feature finding with deisotoping
        fm = oms.FeatureMap()
        feat_chrom = []
        ffm = oms.FeatureFindingMetabo()
        ffm_params = ffm.getDefaults()
        ffm_params.setValue("isotope_filtering_model", "peptides")
        ffm_params.setValue("mass_error_ppm", params['mass_error_ppm'])
        ffm_params.setValue("remove_single_traces", "true")
        ffm_params.setValue("intensity_threshold", params['min_intensity'])
        if params.get('use_gpu', False):
            ffm_params.setValue("use_gpu", "true")  # Enable GPU if available
        ffm.setParameters(ffm_params)
        ffm.run(mass_traces_split, fm, feat_chrom)

        # 5. Feature binning
        fm_binned = bin_features(
            fm, 
            mz_bin_size=params['mz_bin_size'], 
            rt_bin_size=params['rt_bin_size']
        )

        # 6. Normalize by TIC (use binned intensities for sum)
        total_intensity = sum(f.getIntensity() for f in fm_binned)
        if total_intensity > 0:  # Avoid division by zero
            for feat in fm_binned:
                feat.setIntensity(feat.getIntensity() / total_intensity * 1e6)

        return fm_binned, sample_id  # ← Modified return statement

    except Exception as e:
        print(f"Error processing {mzML_path}: {str(e)}", file=sys.stderr)
        return None, None  # ← Return tuple even on failure

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input mzML file")
    parser.add_argument("--output", required=True, help="Output feature file")
    parser.add_argument("--config", default="params.json", help="Parameter file")
    args = parser.parse_args()

    params = load_params(args.config)
    features, sample_id  = process_mzML(args.input, params)
    
    if features:
        # Save features (e.g., as Feather or CSV)
        pd.DataFrame({
            'mz': [f.getMZ() for f in features],
            'rt': [f.getRT() for f in features],
            'intensity': [f.getIntensity() for f in features],
            'charge': [f.getCharge() for f in features],
            'sample_id': sample_id
        }).to_feather(args.output)

if __name__ == "__main__":
    main()
