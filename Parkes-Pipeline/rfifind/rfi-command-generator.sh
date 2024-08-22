#!/bin/bash
date=10

# Setting the path
path="/fred/oz203/data/PX094/J0523-2529/2022OCTS$date/raw/"
cd "${path}mask"

# clear .txt file if previous commands exist
echo > /home/ojohnson/reduc-parkes/sjobs/rfi-jobs/rfi-commands-$date.txt

for filename in ${path}*.sf; do
    # Extract the base name of the file (without the directory path and extension)
    base_name=$(basename "$filename" .sf)
    echo "Generating rfi command for ${base_name}..."
    
    # Check if .mask file already exists
    if [ -e "${base_name}_rfifind.mask" ]; then
        echo "Mask file already exists for ${base_name}, skipping rfifind..."
    else
        # print the command to the output file
        echo rfifind -time 1 -o "${base_name}_t1" "$filename" >> /home/ojohnson/reduc-parkes/sjobs/rfi-jobs/rfi-commands-$date.txt
    fi
done