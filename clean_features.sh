#!/bin/bash
#SBATCH --job-name=clean_features
#SBATCH --output=logs/clean_features_%j.out
#SBATCH --error=logs/clean_features_%j.err
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G

#Set Paths
INPUT="/scratch/prj/bmb_doping/msc_project/outputs/merged_features.csv"
OUTPUT="/scratch/prj/bmb_doping/msc_project/outputs/feature_table_clean.parquet"

# Run processing
python clean_features.py \
  --input "$INPUT" \
  --output "$OUTPUT" \
  --chunksize 500  # Adjust based on memory
