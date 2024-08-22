#!/bin/bash
date="07"

working_directory=$(pwd)
run_path="sbatch_scripts_"$date""
echo "Working directory: $working_directory"
mkdir -p "$run_path"
echo "Command file location is: $working_directory/commands-"$date".txt"

path="/fred/oz203/data/PX094/J0523-2529/2022OCTS"$date"/raw/"
cd "$path" || { echo "Error: Unable to change to the specified directory." ; exit 1; }
echo "Number of .fft files in ${path}: $(ls -1 *.fft | wc -l)"

fft_files=$(ls -1 *.fft | wc -l)
i=0

#  Iterate over .fft files in the directory
for file in *.fft; do
    base_name="${file%.*}"
    # Check if there are matching files
    if [ -e "$file" ]; then
        # Check if the accelsearch files have already been produced.
        if [ ! -e "${base_name}_ACCEL_200" ]; then
            echo "accelsearch $file" >> "${working_directory}/commands-$date.txt"
        fi
    else
        echo "No .fft files found in the specified directory."
        exit 1
    fi
    i=$((i+1))
    percentage=$((i * 100 / fft_files))
    # Print loading bar
    echo -ne "Progress: ["
    for ((j=0; j<percentage/2; j++)); do
        echo -ne "#"
    done
    for ((j=percentage/2; j<50; j++)); do
        echo -ne " "
    done
    echo -ne "] $percentage% \r"
done

echo ""

mkdir -p "sbatch_scripts_"$date""
command_file="$working_directory/commands-$date.txt"
folder="$working_directory/sbatch_scripts_"$date""

# check if file is there 
if [ -e "$command_file" ]; then
    echo "Command file exists."
else
    echo "Command file does not exist."
    exit 1
fi

total_commands=$(wc -l < "$command_file")
commands_per_job=200
echo "Total commands to execute: $total_commands"
echo "Commands per job: $commands_per_job"

# Number of sbatch jobs
total_jobs=$((total_commands / commands_per_job))

# Loop through each sbatch job
for ((i = 0; i < total_jobs; i++)); do
    start=$((i * commands_per_job + 1))
    end=$(((i + 1) * commands_per_job))
    
    # Generate sbatch script for each job
    sbatch_script="$folder/acelsearch_$i.sbatch"
    echo "#!/bin/bash" > "$sbatch_script"
    echo "#SBATCH --job-name=acl_srch$i" >> "$sbatch_script"
    echo "#SBATCH --output=$folder/acelsearch_$i.out" >> "$sbatch_script"
    echo "#SBATCH --error=$folder/acelsearch_$i.err" >> "$sbatch_script"
    echo "#SBATCH --time=1-00:00:00" >> "$sbatch_script"
    echo "#SBATCH --mem=100G" >> "$sbatch_script"
    echo "#SBATCH --ntasks=1" >> "$sbatch_script"
    echo "" >> "$sbatch_script"

    # Add commands to sbatch script
    echo "cd /fred/oz203/data/PX094/J0523-2529/2022OCTS"$date"/raw/" >> "$sbatch_script"
    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"
    echo "" >> "$sbatch_script"

    sed -n "${start},${end}p" "$command_file" >> "$sbatch_script"

    echo"" >> "$sbatch_script"
    sbatch "$sbatch_script"
done

echo "Submitted $total_jobs sbatch jobs."
