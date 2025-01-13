#!/bin/bash

# Get the input path from the first argument
path=$1  


# Ensure the path exists and is a directory
if [ ! -d "$path" ]; then
    echo "Error: Specified path does not exist or is not a directory."
    exit 1
fi

# Iterate over .dat files in the specified path
for filename in $(find "$path" -type f -name "*DM*.dat"); do
    # If red reduction is already complete skip, .dat file. 
    if [[ "$filename" == *"_red"* ]]; then
    echo "Skipping $filename"
        continue
    fi

    if [ -f "$filename" ]; then
        if command -v realfft >/dev/null 2>&1; then
            # Extract the base name 
            basename="${filename%.dat}"

            # echo "Processing file: $filename"

            # Perform realfft on the .dat file
            realfft "$filename"

            # Define the fft file and process with rednoise
            fft_file="${basename}.fft"
            rednoise "$fft_file"

            # Define the red file and process with realfft again
            red_file="${basename}_red.fft"
            # realfft "$red_file"

            # Remove the original .dat file
            rm "$filename"
            rm "${basename}.fft"
            # rm "${basename}.inf"

            if [ ! -f "${basename}_red.inf" ]; then
                mv "${basename}.inf" "${basename}_red.inf"
            fi

        else
            echo "Error: realfft command not found or not executable"
            exit 1
        fi
    else
        echo "No .dat files found matching pattern in $path"
    fi
done
