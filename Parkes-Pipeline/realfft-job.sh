path="/fred/oz203/data/PX094/J0523-2529/2022OCTS07/raw/"
cd $path  # Removed unnecessary quotes

# Source psrhome.sh script
source /fred/oz002/psrhome/scripts/psrhome.sh

# Iterate over .dat files in the specified path
for filename in "${path}"/*DM*.dat; do 
    if [ -f "$filename" ]; then  # Check if the file exists
        # Check if realfft command is executable
        if command -v realfft >/dev/null 2>&1; then
            # Execute realfft command with the filename
            realfft "$filename"
        else
            echo "Error: realfft command not found or not executable"
            exit 1
        fi
    else
        echo "Error: $filename does not exist or is not a regular file"
    fi
done