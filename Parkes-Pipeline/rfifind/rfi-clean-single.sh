source /fred/oz002/psrhome/scripts/psrhome.sh

filename="/fred/oz203/data/PX094/J0523-2529/2022OCTS07/raw/uwl_221109_114040_0.sf"
base_name=$(basename "$filename" .sf)

# Define the list of times
times=("1" "10" "100" "200")

# Iterate over each time value
for time in "${times[@]}"; do
    rfifind -time "$time" -o "${base_name}_t${time}" "$filename"
done
