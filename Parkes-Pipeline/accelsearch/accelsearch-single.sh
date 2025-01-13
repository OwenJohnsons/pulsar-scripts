#!/bin/bash

file=$1
cpu_cores=$2

mjd_0_5=$(echo "scale=10; 2456577.64636 - 2400000.5" | bc)
orb_period="16.5"
f_spin=1000         # Hz
k2=190300          # m/s
P_orb=59454.432    # seconds
q=0.61              # mass ratio

calculate_orbital_phase() {
    local mjd_observed=$1
    local mjd_0_5=$2
    local orbital_period=$3

    local orb_P_day=$(awk "BEGIN {print $orbital_period / 24}") # Convert to days
    local subtract_mjd=$(echo "scale=10; $mjd_observed - $mjd_0_5" | bc -l)
    local phase=$(echo "scale=10; $subtract_mjd / $orb_P_day" | bc -l)
    echo $(echo "$phase" | awk '{print $1 - int($1)}')
}

calculate_z() {
    local f_spin="$1"
    local k2="$2"
    local P_orb="$3"
    local q="$4"
    local t="$5"
    local t_asc="$6"
    local T_obs="$7"

    local c=299792458
    local z=$(awk -v f_spin="$f_spin" -v k2="$k2" -v P_orb="$P_orb" -v q="$q" \
                 -v t="$t" -v t_asc="$t_asc" -v T_obs="$T_obs" -v c="$c" '
    BEGIN {
        a_sin_i = (k2 * P_orb) / (2 * 3.14159265359 * q);
        sin_term = sin(2 * 3.14159265359 * (t_asc) / P_orb);
        f_dot = f_spin * (4 * 3.14159265359^2 * a_sin_i) / (c * P_orb^2) * sin_term;
        z = f_dot * T_obs^2;
        print z;
    }')
    echo "$z"
}

# find "$path" -name "*_red.fft" | while read -r file; do
basename=$(basename "$file" _red.fft)
dirpath=$(dirname "$file")

infofile="${dirpath}/${basename}_red.inf"
if [ -e "$infofile" ]; then
    date=$(grep "MJD" "$infofile" | awk '{print $NF}')
    time_samples=$(grep "Number of bins in the time series" "$infofile" | awk '{print $NF}')
    tres=$(grep "time series bin" "$infofile" | awk '{print $NF}')
    tobs=$(awk -v ts="$time_samples" -v tr="$tres" 'BEGIN {print ts * tr}')

    start_phase=$(calculate_orbital_phase "$date" "$mjd_0_5" "$orb_period")
    end_phase=$(calculate_orbital_phase "$(echo "$date + $tobs / 86400" | bc -l)" "$mjd_0_5" "$orb_period")

    t_z=$(awk -v porb="$P_orb" -v phase="$start_phase" 'BEGIN {print porb * phase}')
    z_val=$(calculate_z "$f_spin" "$k2" "$P_orb" "$q" "$t_z" "$t_z" "$tobs")
    z_val=$(printf "%.0f" "$z_val")

    echo "--- Z Parameter Calculation ---"
    echo "MJD: $date"
    echo "Time samples: $time_samples"
    echo "Time resolution (s): $tres"
    echo "Observation time (s): $tobs"
    echo "Start phase: $start_phase"
    echo "End phase: $end_phase"
    echo "Time since ascending node (s): $t_z"
    echo "Z value: $z_val"

    if [ $(echo "$z_val < 200" | bc) -eq 1 ]; then
        echo "NOTE: Z value is less than 200, setting to 200"
        z_val=200
    elif [ $(echo "$z_val > 1200" | bc) -eq 1 ]; then
        echo "NOTE: Z value is greater than 1200, setting to 1200"
        z_val=1200
    fi

    accelsearch -zmax "$z_val" -ncpus "$cpu_cores" "$file"
else
    echo "Info file not found for $basename"
fi

