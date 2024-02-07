path="/fred/oz203/data/PX094/J0523-2529/2022OCTS07/raw/"
cd "${path}"
source /fred/oz002/psrhome/scripts/psrhome.sh

for filename in ${path}*.sf; do
    # Extract the base name of the file (without the directory path and extension)
    base_name=$(basename "$filename" .sf)
    mask_name="mask/${base_name}_t1_rfifind.mask"
    prepsubband_name="${base_name}_prepsubband_DM0.00.dat"
    # Check if mask exists
    if [ -e "$mask_name" ]; then
        echo "Mask found for ${base_name}!"
        if [ -e "$prepsubband_name" ]; then
            echo "Prepsubband file already exists for ${base_name}, skipping this file. "
            continue
        else
            echo "Prepsubband file does not exist for ${base_name}, starting prepsubband."
            echo "Output file: ${base_name}prepsubband"
            prepsubband -psrfits -nsub 3328 -lodm 0 -dmstep 0.492 -numdms 200 -mask "$mask_name" -o "${base_name}_prepsubband" "$filename"
        fi
    else
        echo "No mask found for ${base_name}."
        exit 1
    fi
done