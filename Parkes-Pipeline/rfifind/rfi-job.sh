source /fred/oz002/psrhome/scripts/psrhome.sh

path="/fred/oz203/data/PX094/2022OCTS10/raw/"
cd "${path}mask"

for filename in ${path}*.sf; do
    # Extract the base name of the file (without the directory path and extension)
    base_name=$(basename "$filename" .sf)
    rfifind -time 1 -o "${base_name}_t1" "$filename"
done