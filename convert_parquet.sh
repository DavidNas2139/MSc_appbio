#!/bin/bash
#SBATCH --job-name=csv_to_parquet
#SBATCH --output=logs/convert_%j.out
#SBATCH --error=logs/convert_%j.err
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G  # Adjust based on chunksize

# Run conversion
python csv_to_parquet.py \
  --input "/scratch/prj/bmb_doping/msc_project/outputs/merged_features.csv" \
  --output "/scratch/prj/bmb_doping/msc_project/outputs/feature_table.parquet" \
  --chunksize 1000  # Higher = faster but needs more RAM
