#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import numpy as np

def apply_80pct_rule(df):
    """Filter features present in ≥80% of samples"""
    threshold = 0.5 * len(df)
    return df.loc[:, (df != 0).sum() >= threshold]

def process_large_csv(input_path, output_path, chunksize=1000):
    """Process CSV in chunks with 80% rule"""
    # Initialize variables
    valid_features = set()
    chunks = []
    
    # First pass: Identify features passing 80% rule in any chunk
    for chunk in pd.read_csv(input_path, chunksize=chunksize, index_col='sample_id'):
        chunk_features = (chunk != 0).sum()
        valid_features.update(chunk_features[chunk_features >= 0.5 * len(chunk)].index.tolist())
    
    # Second pass: Filter and process chunks
    for chunk in pd.read_csv(input_path, chunksize=chunksize, index_col='sample_id'):
        filtered = chunk[list(valid_features)]  # Only keep validated features
        chunks.append(filtered)
    
    # Combine and save
    final_df = pd.concat(chunks)
    final_df.to_parquet(output_path)  # Parquet is better for HPC workflows
    print(f"Saved cleaned data to {output_path}")
    print(f"Final shape: {final_df.shape}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output path (should end with .parquet)")
    parser.add_argument("--chunksize", type=int, default=1000, help="Rows per chunk")
    args = parser.parse_args()
    
    process_large_csv(args.input, args.output, args.chunksize)
