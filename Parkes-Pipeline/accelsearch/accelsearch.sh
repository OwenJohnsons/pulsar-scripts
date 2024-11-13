#!/bin/bash

path=$1

# WARNING: HARD-CODED VALUES FOR J0529
mjd_0_5=$(echo "2456577.64636 - 2400000.5" | bc)
orb_period="16.5"
f_spin=1000         # Hz
k2=190300          # m/s
P_orb=59454.432    # seconds
q=0.61              # mass ratio


calculate_orbital_phase() {
    local mjd_observed=$1  # Observed MJD
    local mjd_0_5=$2       # MJD when the phase is 0.5
    local orbital_period=$3 # Orbital period in hours

    orb_P_day=$(awk "BEGIN {print $orb_period / 24}") # Convert orbital period to days 
    subtract_mjd=$(echo "$mjd_observed - $mjd_0_5" | bc -l)
    phase=$(echo "$subtract_mjd / $orb_P_day" | bc -l)
    echo $(echo "$phase" | awk '{print $1 - int($1)}')
}

calculate_z() {
    # Parameters
    local f_spin="$1"  # Spin frequency (Hz)
    local k2="$2"      # Semi-amplitude of the companion's radial velocity (m/s)
    local P_orb="$3"   # Orbital period (seconds)
    local q="$4"       # Mass ratio
    local t="$5"       # Current time (seconds)
    local t_asc="$6"   # Time of ascending node (seconds)
    local T_obs="$7"   # Length of observation (seconds)

    # Constants
    local c=299792458  # Speed of light (m/s)

    # Perform all calculations using awk
    local z=$(awk -v f_spin="$f_spin" -v k2="$k2" -v P_orb="$P_orb" -v q="$q" \
                 -v t="$t" -v t_asc="$t_asc" -v T_obs="$T_obs" -v c="$c" '
    BEGIN {
        # Compute a_sin_i
        a_sin_i = (k2 * P_orb) / (2 * 3.14159265359 * q);

        # Compute sin_term
        sin_term = sin(2 * 3.14159265359 * (t_asc) / P_orb);


        # Compute f_dot
        f_dot = f_spin * (4 * 3.14159265359^2 * a_sin_i) / (c * P_orb^2) * sin_term;

        # Compute z
        z = f_dot * T_obs^2;
      
        # Return z
        print z;
    }')

    # Return result
    echo "$z"
}

# Find rednoise reduced FFTs in the given path
for file in $(find "$path" -name "*_red.fft"); do
    basename=$(basename "$file" _red.fft)
    dirpath=$(dirname "$file")

    infofile="${dirpath}/${basename}_red.inf"
    # Check if the info file exists
    if [ -e "$infofile" ]; then
        # Pull date from the file last col 
        date=$(grep "MJD" "$infofile" | awk '{print $NF}')
        time_samples=$(grep "Number of bins in the time series" "$infofile" | awk '{print $NF}')
        tres=$(grep "time series bin" "$infofile" | awk '{print $NF}')
        tobs=$(awk -v ts="$time_samples" -v tr="$tres" 'BEGIN {print ts * tr}')

        start_phase=$(calculate_orbital_phase "$date" "$mjd_0_5" "$orb_period")
        end_phase=$(calculate_orbital_phase "$(echo "$date + $tobs / 86400" | bc -l)" "$mjd_0_5" "$orb_period")

        # ascending time P_orb*start_phase
        t_z=$(awk -v porb="$P_orb" -v phase="$start_phase" 'BEGIN {print porb * phase}')
        z_val=$(calculate_z "$f_spin" "$k2" "$P_orb" "$q" "$t_z" "$t_z" "$tobs")

        
        echo "--- Z parameter Calculation ---"
        echo "MJD: $date"
        echo "Time samples: $time_samples"
        echo "Time resolution (s): $tres"
        echo "Observation time (s): $tobs"
        echo "Start phase: $start_phase"
        echo "End phase: $end_phase"
        echo "Time since ascending node (s): $t_z"
        echo "Z value: $z_val"
        # if less than 200 set z value to 200
        if [ $(echo "$z_val < 200" | bc) -eq 1 ]; then
            echo "NOTE: Z value is less than 200, setting to 200"
            z_val=200
        fi
    else
        echo "Info file not found for $basename"
    fi
done
