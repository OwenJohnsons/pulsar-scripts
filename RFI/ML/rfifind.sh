#placeholder file to build search pipeline around 

for filename in /fred/oz203/data/PX094/J0523-2529/2022OCTS07/raw/*.sf; do
    # Extract the base name of the file (without the directory path and extension)
    base_name=$(basename "$filename" .sf)
    rfifind -time 10 -o "${base_name}" "$filename"
done
