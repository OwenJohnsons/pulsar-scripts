# Code Purpose: Calculate the orbital phase of a set of .add.sf files

#!/bin/bash

path=$1

# Use find to locate all .add.sf files
file_paths=$(find "$path" -name "*.add.sf")
echo 'Number of files found:'  $(echo "$file_paths" | wc -l)

# Convert BJD ephemeris (at 0.5) to MJD
mjd_0_5=$(echo "2456577.64636 - 2400000.5" | bc)
orb_period="16.5"
echo "--- Phases Covered ---" 

# Function to calculate orbital phase
calculate_orbital_phase() {
    local mjd_observed=$1  # Observed MJD
    local mjd_0_5=$2       # MJD when the phase is 0.5
    local orbital_period=$3 # Orbital period in hours

    orb_P_day=$(awk "BEGIN {print $orb_period / 24}") # Convert orbital period to days 
    subtract_mjd=$(echo "$mjd_observed - $mjd_0_5" | bc -l)
    phase=$(echo "$subtract_mjd / $orb_P_day" | bc -l)
    echo $(echo "$phase" | awk '{print $1 - int($1)}')
}

declare -A file_groups

# Group files by their patterns
for file_path in $file_paths; do
    if [[ "$file_path" =~ ([0-9]{6}_[0-9]{6}) ]]; then
        pattern="${BASH_REMATCH[1]}"
        file_groups["$pattern"]+="$file_path "
    fi
done

# Loop through each pattern and calculate orbital phases
for pattern in "${!file_groups[@]}"; do
    sum_length=0  # Initialize sum to 0 for each file group
    first_date=""  # Initialize variable to store the first date
    
    # Loop through all files associated with the current pattern
    for file in ${file_groups[$pattern]}; do
        paz_command=$(vap -c date,length "$file" | awk "NR==2")
        date=$(echo "$paz_command" | awk '{print $2}')
        length=$(echo "$paz_command" | awk '{print $3}')
        
        # If this is the first file, store its date
        if [ -z "$first_date" ]; then
            first_date="$date"
        fi
        
        # Add the current file's length to the total sum for this group
        sum_length=$(echo "$sum_length + $length" | bc)
    done

    # Convert the first date to MJD
    if [ -n "$first_date" ]; then
        # Convert the first date to Unix timestamp
        unix_time=$(date -d "$first_date" +%s)
        mjd=$(echo "$unix_time / 86400 + 40587" | bc -l)
        
        final_mjd=$(echo "$mjd + $sum_length / 86400" | bc -l)
        
        start_phase=$(calculate_orbital_phase "$mjd" "$mjd_0_5" "$orb_period_days")
        final_phase=$(calculate_orbital_phase "$final_mjd" "$mjd_0_5" "$orb_period_days")
        echo $start_phase : $final_phase
        # write to file
        echo "$pattern : $start_phase : $final_phase" >> orbital_phase.txt
    fi
done
