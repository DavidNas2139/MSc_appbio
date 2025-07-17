#!/usr/bin/env python3
import pandas as pd
import argparse

def convert_csv_to_parquet(input_path, output_path, chunksize=1000):
    """
    Convert large CSV to Parquet in chunks without filtering
    """
    # Get columns without loading full file
    header = pd.read_csv(input_path, nrows=0)
    columns = header.columns.tolist()
    
    # Process in chunks
    chunks = []
    for chunk in pd.read_csv(input_path, chunksize=chunksize, low_memory=False):
        chunks.append(chunk)
    
    # Combine and save
    pd.concat(chunks).to_parquet(output_path)
    print(f"Successfully converted {len(chunks)} chunks to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output .parquet path")
    parser.add_argument("--chunksize", type=int, default=1000, help="Rows per chunk")
    args = parser.parse_args()
    
    if not args.output.endswith('.parquet'):
        raise ValueError("Output path must end with .parquet")
    
    convert_csv_to_parquet(args.input, args.output, args.chunksize)
