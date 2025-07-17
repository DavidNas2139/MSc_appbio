# Preprocessing pipeline:

1. Convert the .raw fiels to .mzml files, using raw_to_mzml.sh script 
2. Create and activate the conda environment from metabolomics.yml
3. Run feature detection, peak detection, binning, deisotoping, binning, normalization with mzml_to_feather.sh
4. Once complete, Run merge_featutes.sh to merge all the .feather files into a single feature table
5. Convert the .csv file to .parquet as it is too big using convert_parquet.sh
6. Extract the sample ids using sampleId_exract.py
