#!/bin/bash
#SBATCH --job-name=merge_features
#SBATCH --output=logs/merge_%j.out
#SBATCH --error=logs/merge_%j.err
#SBATCH --time=2:00:00           # Adjust based on expected runtime
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4        # Helps with pandas operations               
#SBATCH --partition=cpu    


# Set paths (modify these)
INPUT_DIR="/scratch/prj/bmb_doping/msc_project/outputs/feathers/same_athlete"
OUTPUT_PATH="/scratch/prj/bmb_doping/msc_project/outputs/merged_features_same.csv"

# Run the merging script
python /scratch/prj/bmb_doping//msc_project/scripts/merge_features.py \
  --input_dir "$INPUT_DIR" \
  --output "$OUTPUT_PATH"

# Verify output
if [ -f "$OUTPUT_PATH" ]; then
    echo "Merge successful. Output at $OUTPUT_PATH"
    # Optional: Print summary
    python -c "import pandas as pd; df = pd.read_csv('$OUTPUT_PATH', nrows=5); print(df.head())"
else
    echo "Error: Merge failed - output file not created"
    exit 1
fi
