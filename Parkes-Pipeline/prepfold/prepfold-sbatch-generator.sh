commands_file="/fred/oz203/data/PX094/J0523-2529/cand_plot/accelsearchcands/sifted/prepfold_commands.txt"
working_directory=$(pwd)
path="run1"
mkdir -p "$path"

total_commands=$(wc -l < "$commands_file")
echo "Total commands to execute: $total_commands"

# Loop through each line in the commands file
while IFS= read -r command; do
    # Generate a unique sbatch script for each command
    job_id=$(echo "$command" | md5sum | cut -d ' ' -f 1) # Generate a unique hash for the command
    sbatch_script="${path}/prepfold_${job_id}.sbatch"

    echo "#!/bin/bash" > "$sbatch_script"
    echo "#SBATCH --job-name=folding_${job_id}" >> "$sbatch_script"
    echo "#SBATCH --output=$working_directory/$path/folding_${job_id}.out" >> "$sbatch_script"
    echo "#SBATCH --error=$working_directory/$path/folding_${job_id}.err" >> "$sbatch_script"
    echo "#SBATCH --time=01:30:00" >> "$sbatch_script"
    echo "#SBATCH --mem=600MB" >> "$sbatch_script"
    echo "#SBATCH --ntasks=1" >> "$sbatch_script"
    echo "" >> "$sbatch_script"

    # Add environment setup and the command to the sbatch script
    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"
    echo "" >> "$sbatch_script"
    echo "$command" >> "$sbatch_script"

    # Submit the SBATCH script
    sbatch "$sbatch_script"
done < "$commands_file"

echo "Submitted $total_commands sbatch jobs."
