#!/bin/bash
# Usage merge-fits.sh <input_dir> 

path=$1
output_dir="/lorule/scratch/oaj00001/data"

to_mjd() {
    python3 -c "
from datetime import datetime
from astropy.time import Time
dt = datetime.fromisoformat('$1')
t = Time(dt)
print(f'{t.mjd:.5f}')  # MJD accurate to the second
"
}

# fits_files=$(ls $path/*.fits | sort -t '_' -k5,5n -k6,6n)
declare -A groups

while IFS= read -r filepath; do
    filename=$(basename "$filepath")
    key=$(echo "$filename" | awk -F'_' '{print $1"_"$2"_"$3"_"$4"_"$5}')
    groups["$key"]+="$filepath "
done < <(ls $path/*.fits | sort)

for key in "${!groups[@]}"; do
    echo "Group: $key"

    set -- ${groups[$key]}
    source_name=$(vap -c name "$1" | awk 'NR == 2 {print $2}')
    obs_date=$(vap -c date "$1" | awk 'NR == 2 {print $2}')
    obs_mjd=$(to_mjd "$obs_date")
    fcntr=$(vap -c fcntr "$1" | awk 'NR == 2 {print $2}')

    # LF = 820, L = 1450, S = 2200 
    if [[ $fcntr -lt 1000 ]]; then
        band="850MHz"
    elif [[ $fcntr -lt 2000 ]]; then
        band="Lband"
    else
        band="Sband"
    fi

    comb_length=$(vap -c length ${groups[$key]} | awk '{sum+=$2}END{printf "%.3f\n",sum}') # Combine the length for all the files in a group. 
    comb_nrows=$(psredit -c sub:nrows ${groups[$key]} | awk -F= '{sum+=$2}END{print sum}')

    output_fname="${source_name}_${obs_mjd}_${band}.fits"
    echo "Output: $output_fname"
    echo "Source: $source_name"
    echo "Date: $obs_date"
    echo "Combined Length: $comb_length s"
    echo "Combined Nrows: $comb_nrows"

    # Merge the files with cat 
    # echo "cat ${groups[$key]} > $output_dir/$output_fname"

    
    echo ""
done