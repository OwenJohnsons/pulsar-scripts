#!/bin/bash

for folder in uwl*/; do
    echo "📂 $folder"

    basename=$(basename "$folder")

    # FFT counts
    declare -A expected_counts=(
        ["0.7-1.9GHz"]=1334
        ["1.9-3.0GHz"]=200
        ["3.0-4.0GHz"]=80
    )

    # Loop through each frequency range
    for range in "${!expected_counts[@]}"; do
        prepdata_dir="$basename/prepdata/$range"

        # Count FFT files
        fft_count=$(find "$prepdata_dir/" -name "${basename}*_red.fft" -type f | wc -l)

        datred_count=$(find "$prepdata_dir/" -name "${basename}*_red.dat" -type f | wc -l)
        dat_count=$(find "$prepdata_dir/" -name "${basename}*.dat" -type f ! -name *_red* | wc -l)

        # Check if the FFT count matches the expected value
        if [[ $fft_count -eq ${expected_counts[$range]} ]]; then
            fft_check="✔"
        else
            fft_check="✗"
        fi

        accel_cand_count=$(find "$prepdata_dir/" -name "*_ACCEL*" -type f ! -name "*.txtcand" ! -name "*.cand" | wc -l)

        # Check if the ACCEL count matches the expected value
        if [[ $accel_cand_count -eq ${expected_counts[$range]} ]]; then
            accel_check="✔"
        else
            accel_check="✗"
        fi

        # Print tree structure
        echo "  └── $range"
        echo "      ├── FFT files: $fft_count $fft_check"
        echo "      ├── ACCEL: $accel_cand_count $accel_check"
        echo "      ├── DAT files: $dat_count"
        echo "      └── DAT_RED files: $datred_count"
    done
done
