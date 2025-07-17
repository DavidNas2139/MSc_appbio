#!/bin/bash
#SBATCH --job-name=mzml_processing
#SBATCH --output=logs/%A_%a.out  # %A=jobID, %a=arrayIndex
#SBATCH --error=logs/%A_%a.err
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --array=1-2000%9 # Replace N with total files, %10 limits concurrent jobs

# Directory setup
MZML_DIR="/scratch/prj/bmb_doping/msc_project/outputs/mzml/same_athlete"
FEATHER_DIR="/scratch/prj/bmb_doping/msc_project/outputs/feathers/same_athlete"
CONFIG="/scratch/prj/bmb_doping/msc_project/config/params.json"

# Get all .mzML files into an array
FILES=($MZML_DIR/*.mzML)

# Verify array index is within bounds
if [ $SLURM_ARRAY_TASK_ID -le ${#FILES[@]} ]; then
    INPUT_FILE="${FILES[$SLURM_ARRAY_TASK_ID-1]}"
    FILENAME=$(basename "$INPUT_FILE" .mzML)
    SAMPLE_ID="${FILENAME%.mzML}" 
    
    echo "Processing $INPUT_FILE → $OUTPUT_FILE"
    python /scratch/prj/bmb_doping//msc_project/scripts/process_mzml.py \
        --input "$INPUT_FILE" \
        --output "$FEATHER_DIR/${SAMPLE_ID}.feather" \
        --config "$CONFIG"
else
    echo "Array index $SLURM_ARRAY_TASK_ID out of range (max ${#FILES[@]})"
fi
