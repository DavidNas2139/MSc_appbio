#!/usr/bin/env python3
"""
Script to extract sample IDs from mzML files and save to CSV
"""

import os
import csv
import xml.etree.ElementTree as ET
from pathlib import Path


def decode_mzml_id(encoded_id):
    """Decodes mzML-specific encoding like *x0020* to spaces"""
    if not encoded_id:
        return encoded_id
    # Split at each _x followed by 4 hex digits
    parts = []
    current_pos = 0
    while True:
        start = encoded_id.find('_x', current_pos)
        if start == -1:
            parts.append(encoded_id[current_pos:])
            break
        # Check if we have 4 hex digits after _x
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
    """Extracts The Sample Id from the file and Decodes it"""
    try:
        # Parse the file
        tree = ET.parse(mzml_file)
        root = tree.getroot()
        # Handle namespaces
        ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {'ns': ''}
        # Find sample element
        sample = root.find('.//ns:sample', ns) or root.find('.//sample')
        if sample is not None:
            encoded_id = sample.get('id')
            return decode_mzml_id(encoded_id)
        return None
    except ET.ParseError as e:
        print(f"Error parsing {mzml_file}: {e}")
        return None
    except Exception as e:
        print(f"Error processing {mzml_file}: {e}")
        return None


def main():
    # Define paths
    mzml_dir = Path("/scratch/prj/bmb_doping/msc_project/outputs/mzml")
    output_file = Path("/scratch/prj/bmb_doping/msc_project/outputs/sample_ids.csv")
    
    # Check if input directory exists
    if not mzml_dir.exists():
        print(f"Error: Directory {mzml_dir} does not exist")
        return 1
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Find all .mzml files
    mzml_files = list(mzml_dir.glob("*.mzML"))
    
    if not mzml_files:
        print(f"No .mzml files found in {mzml_dir}")
        return 1
    
    print(f"Found {len(mzml_files)} .mzml files")
    
    # Extract sample IDs and store results
    results = []
    
    for mzml_file in mzml_files:
        print(f"Processing {mzml_file.name}...")
        sample_id = get_sample_id(mzml_file)
        
        if sample_id:
            results.append({
                'filename': mzml_file.name,
                'sample_id': sample_id
            })
            print(f"  Found sample ID: {sample_id}")
        else:
            print(f"  No sample ID found in {mzml_file.name}")
            results.append({
                'filename': mzml_file.name,
                'sample_id': 'N/A'
            })
    
    # Write results to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['filename', 'sample_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\nResults saved to {output_file}")
    print(f"Processed {len(results)} files")
    
    return 0


if __name__ == "__main__":
    exit(main())
