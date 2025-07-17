#!/bin/bash
#SBATCH --job-name=raw2mzml            # Job name
#SBATCH --output=conversion_%j.log     # Output log (%j = job ID)

# Set the directory with the .raw files
RAW_DIR="/scratch/prj/bmb_doping/msc_project/originals/same_athlete"
OUTPUT_DIR="/scratch/prj/bmb_doping/msc_project/outputs/mzml/same_athlete"

# Image settings
DOCKER_URI="docker://proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses"
SIF_IMAGE="${OUTPUT_DIR}/pwiz_latest.sif"
#Pull the image
echo "Pulling Singularity image..."
singularity pull "$SIF_IMAGE" "$DOCKER_URI"

# Loop through each .raw file in the input directory
for raw_file in "$RAW_DIR"/*.raw; do
    base_name=$(basename "$raw_file" .raw)
    echo "[$(date)] Converting $base_name..."
    
    singularity exec \
      --bind "$RAW_DIR:/input,$OUTPUT_DIR:/output" \
      "$SIF_IMAGE" \
      wine msconvert "/input/${base_name}.raw" \
        --mzML \
        --32 \
        --filter "peakPicking true 1-" \
        -o /output
done

echo "✅ Conversion complete. mzML files saved to: $OUTPUT_DIR"
