#!/bin/bash

path=$1

cand_path="/fred/oz203/data/PX094/J0523-2529/cand_plot/accelsearchcands"

# Find all folders matching "uwl*" and iterate over them
find "$path" -type d -name "uwl*" | while read -r folder; do
    basename=$(basename "$folder")
    echo "Processing $folder"

    # Find all .txtcand files in the current folder
    find "$folder" -name "*.txtcand" | while read -r cand_file; do
        accel_file="${cand_file%.txtcand}"
        accel_file_output=$(basename "${accel_file/_red/}")

        # split cand_file by _red 
        info_file="${cand_file/_red*/_red.inf}"
        info_file_output=$(basename "${info_file/_red/}")

        # Determine the subfolder name
        subfolder=$(basename "$(dirname "$accel_file")")

        # Create subfolder if it doesn't exist
        mkdir -p "$cand_path/$basename/$subfolder"

        # Copy ACCEL search and info files to the candidate path
        if [ -f "$accel_file" ]; then
            cp "$accel_file" "$cand_path/$basename/$subfolder/$accel_file_output"
            cp "$info_file" "$cand_path/$basename/$subfolder/$info_file_output"
        else
            echo "ACCEL search file not found for $cand_file"
        fi
    done
done
