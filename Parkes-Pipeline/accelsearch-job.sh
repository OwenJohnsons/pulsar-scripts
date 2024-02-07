source /fred/oz002/psrhome/scripts/psrhome.sh

# Set the directory path
directory_path="/fred/oz203/data/PX094/J0523-2529/2022OCTS07/raw/"

# Change to the specified directory
cd "$directory_path" || { echo "Error: Unable to change to the specified directory." ; exit 1; }
pwd

# Iterate over .fft files in the directory
for file in *.fft; do
    # Check if there are matching files
    if [ -e "$file" ]; then
        echo "$file"
        accelsearch "$file"
    else
        echo "No .fft files found in the specified directory."
        exit 1
    fi
done