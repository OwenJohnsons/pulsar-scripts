#!/bin/bash

path=$1

# Use find to locate all .add.sf files
file_paths=$(find "$path" -name "*0.7*.sf" | sort)
echo 'Number of files found:'  $(echo "$file_paths" | wc -l)

# Convert BJD ephemeris (at 0.5) to MJD
mjd_0_5=$(echo "2456577.64636 - 2400000.5" | bc)
orb_period="16.51512"

echo "MJD | Date | Length (hrs) | Phases" > phases.txt

# Function to calculate orbital phase
calculate_orbital_phase() {
    local mjd_observed=$1  # Observed MJD
    local mjd_0_5=$2       # MJD when the phase is 0.5
    local orbital_period=$3 # Orbital period in hours

    orb_P_day=$(awk "BEGIN {print $orbital_period / 24}") # Convert orbital period to days 
    subtract_mjd=$(echo "$mjd_observed - $mjd_0_5" | bc -l)
    phase=$(echo "$subtract_mjd / $orb_P_day - 0.5" | bc -l) # Adjust for phase 0.5 reference

    # Ensure the phase is wrapped between 0 and 1
    adjusted_phase=$(awk "BEGIN {print sprintf(\"%.2g\", ($phase % 1 + 1) % 1)}")

    echo "$adjusted_phase"
}

declare -A file_groups
total_observed_time=0  # Initialize total observed time in seconds
declare -a observations  # Store observations for sorting

# Group files by their patterns
for file_path in $file_paths; do
    if [[ "$file_path" =~ ([0-9]{6}_[0-9]{6}) ]]; then
        pattern="${BASH_REMATCH[1]}"
        file_groups["$pattern"]+="$file_path "
    fi
done

# Print Header
printf "%-10s | %-16s | %-12s | %-12s\n" "MJD" "Date" "Length (hrs)" "Phases"
echo "---------------------------------------------------------------"

# Loop through each pattern and calculate orbital phases and observation times
for pattern in "${!file_groups[@]}"; do
    sum_length=0  # Initialize sum to 0 for each file group
    first_date=""  # Initialize variable to store the first date
    first_mjd=""   # Initialize variable for first MJD

    sorted_files=$(echo "${file_groups[$pattern]}" | tr ' ' '\n' | sort -V)

    # Loop through all files associated with the current pattern
    for file in $sorted_files; do
        paz_command=$(vap -c date,length,stt_imjd,stt_smjd "$file" | awk "NR==2")
        date=$(echo "$paz_command" | awk '{print $2}')
        length=$(echo "$paz_command" | awk '{print $3}')
        mjd_day=$(echo "$paz_command" | awk '{print $4}')
        mjd_time=$(echo "$paz_command" | awk '{print $5}')
        mjd="${mjd_day}.${mjd_time}"

        # If this is the first file, store its date and MJD
        if [ -z "$first_date" ]; then
            first_date="$date"
            first_mjd="$mjd"
        fi
        
        # Add the current file's length to the total sum for this group
        sum_length=$(echo "$sum_length + $length" | bc)
    done

    # Add the total observation length for this group to the overall total
    total_observed_time=$(echo "$total_observed_time + $sum_length" | bc)

    # Convert the first date to MJD
    if [ -n "$first_date" ]; then
    
        final_mjd=$(echo "$mjd + $sum_length / 86400" | bc -l)
        
        start_phase=$(calculate_orbital_phase "$mjd" "$mjd_0_5" "$orb_period")
        final_phase=$(calculate_orbital_phase "$final_mjd" "$mjd_0_5" "$orb_period")

        # Convert length to hours with 2 sig figs
        length_hours=$(awk "BEGIN {print sprintf(\"%.2g\", $sum_length / 3600)}")

        # Store observations for sorting
        observations+=("$first_mjd $first_date $length_hours $start_phase -- $final_phase")
    fi
done

# Sort by MJD
IFS=$'\n' sorted_observations=($(sort -n <<<"${observations[*]}"))
unset IFS

# Print sorted results
for obs in "${sorted_observations[@]}"; do
    mjd=$(echo "$obs" | awk '{print $1}')
    date=$(echo "$obs" | awk '{print $2}')
    length=$(echo "$obs" | awk '{print $3}')
    phases=$(echo "$obs" | awk '{print $4, $5, $6}')

    printf "%-10s | %-16s | %-12s | %-12s\n" "$mjd" "$date" "$length" "$phases"
    echo "$mjd | $date | $length | $phases" >> phases.txt
done

# Convert total observed time from seconds to hours
rounded_total_time=$(awk "BEGIN {print sprintf(\"%.2g\", $total_observed_time / 3600)}")
echo "---------------------------------------------------------------"
echo "Total Observed Time: $rounded_total_time hours"
