#!/bin/bash
#SBATCH -J realfft          # Job name
#SBATCH -o /home/ojohnson/reduc-parkes/sjobs/fft-jobs/fft-output-09.log        # Output file (%j is replaced by the job ID)
#SBATCH -e /home/ojohnson/reduc-parkes/sjobs/fft-jobs/fft-error-09.log         # Error file (%j is replaced by the job ID)
#SBATCH -t 7-00:00:00       # Maximum time in format hh:mm:ss
#SBATCH -n 4        # Number of tasks (cores)
#SBATCH --mem=100G  # Memory per node (optional)

path="/fred/oz203/data/PX094/J0523-2529/2022OCTS10/raw/"
cd $path  # Removed unnecessary quotes

# Source psrhome.sh script
source /fred/oz002/psrhome/scripts/psrhome.sh

# Iterate over .dat files in the specified path
for filename in "${path}"/*DM*.dat; do 
    if [ -f "$filename" ]; then  # Check if the file exists
        fft_file="${filename%.dat}.fft"
        if [ -f "$fft_file" ]; then  # Check if the fft file already exists
            echo "Error: $fft_file already exists, skipping this file"
            continue
        else
            # Check if realfft command is executable
            if command -v realfft >/dev/null 2>&1; then
                # Execute realfft command with the filename
                realfft "$filename"
            else
                echo "Error: realfft command not found or not executable"
                exit 1
            fi
        fi
    else
        echo "Error: $filename does not exist or is not a regular file"
    fi
done