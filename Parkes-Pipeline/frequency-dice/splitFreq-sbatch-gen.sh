#!/bin/bash

# Directory passed as the first argument
directory=$1 

# Find all .sf files
file_paths=$(find "$directory" -name "*add.sf")

# Loop through each found file
for file in $file_paths; do
    # Generate the .sbatch file in the current directory
    sbatch_file="./$(basename "${file%.sf}.sbatch")"
    
    # Create the .sbatch file with the appropriate contents
    cat <<EOL > "$sbatch_file"
#!/bin/bash
#SBATCH --job-name=splitFreqJob
#SBATCH --output=./logs/%x.%j.out
#SBATCH --error=./logs/%x.%j.err
#SBATCH --time=5:00:00  # Adjust time as necessary
#SBATCH --mem=50G         # Adjust memory as necessary
#SBATCH --cpus-per-task=1  # Adjust CPU as necessary

./splitFreq.sh "$file"

EOL

    echo "Created sbatch file: $sbatch_file"
done
