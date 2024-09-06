#!/bin/bash
date="10"

commands_file="rfi-commands-addsearch.txt"

working_directory=$(pwd)
path="rfi_sbatch_scripts_addsearch"
mkdir -p "$path"

total_commands=$(wc -l < "$commands_file")
commands_per_job=1
echo "Total commands to execute: $total_commands"
echo "Commands per job: $commands_per_job"

# Number of sbatch jobs
total_jobs=$((total_commands / commands_per_job))

# Loop through each sbatch job
for ((i = 0; i < total_jobs; i++)); do
    start=$((i * commands_per_job + 1))
    end=$(((i + 1) * commands_per_job))
    
    # Generate sbatch script for each job
    sbatch_script="sbatch_scripts_"$date"/rfi_$i.sbatch"
    echo "#!/bin/bash" > "$sbatch_script"
    echo "#SBATCH --job-name=folding_$i" >> "$sbatch_script"
    echo "#SBATCH --output=$working_directory/$path/rfi_$i.out" >> "$sbatch_script"
    echo "#SBATCH --error=$working_directory/$path/rfi_$i.err" >> "$sbatch_script"
    echo "#SBATCH --time=10:00:00" >> "$sbatch_script"
    echo "#SBATCH --mem=300G" >> "$sbatch_script"
    echo "#SBATCH --ntasks=1" >> "$sbatch_script"
    echo "#SBATCH --mail-type=END" >> "$sbatch_script"   # Email when job ends
    echo "#SBATCH --mail-user=ojohnson@tcd.ie" >> "$sbatch_script"
    echo "" >> "$sbatch_script"

    # Add commands to sbatch script
    echo "cd /fred/oz203/data/PX094/J0523-2529/merged_sf" >> "$sbatch_script"
    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"
    echo "" >> "$sbatch_script"

    sed -n "${start},${end}" "$commands_file" >> "$sbatch_script"

    echo"" >> "$sbatch_script"

    sbatch "$sbatch_script"
done

echo "Submitted $total_jobs sbatch jobs."