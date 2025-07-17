#!/usr/bin/env python3
import os
import pandas as pd
from pathlib import Path

def merge_feathers(input_dir, output_path):
    """
    Merge all Feather files in a directory into one DataFrame.
    
    Args:
        input_dir: Path to directory containing .feather files
        output_path: Path for merged output (Feather or CSV)
    """
    # Find all Feather files recursively
    feather_files = list(Path(input_dir).rglob('*.feather'))
    
    if not feather_files:
        raise FileNotFoundError(f"No .feather files found in {input_dir}")
    
    # Read and merge files
    dfs = []
    for f in feather_files:
        df = pd.read_feather(f)
        df['sample_id'] = f.stem  # Add filename as column
        dfs.append(df)
    
    # Concatenate all DataFrames
    merged = pd.concat(dfs, ignore_index=True)
    
    # Pivot to feature table format (samples x features)
    feature_table = merged.pivot_table(
        index='sample_id',
        columns=['mz', 'rt'],  # Using mz/rt as multi-index
        values='intensity',
        fill_value=0  # Replace missing with 0
    )
    
    # Flatten multi-index columns
    feature_table.columns = [
        f"mz_{mz:.4f}_rt_{rt:.1f}" 
        for mz, rt in feature_table.columns
    ]
    
    # Save merged data
    if output_path.endswith('.feather'):
        feature_table.reset_index().to_feather(output_path)
    else:
        feature_table.to_csv(output_path)
    
    print(f"Merged {len(feather_files)} files -> {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="Directory with .feather files")
    parser.add_argument("--output", required=True, help="Output path (.feather or .csv)")
    args = parser.parse_args()
    
    merge_feathers(args.input_dir, args.output)
