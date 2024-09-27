#!/bin/bash

sf_path=$1
commands_file="${sf_path}/masks/rfi-commands.txt"

sbatch_path="${sf_path}/masks/sbatch_scripts"
mkdir -p "$sbatch_path"

# Count total number of commands
# total_commands=$(cat -v "${sf_path}/masks/rfi-commands.txt")
# echo "Total commands to execute: $total_commands"

echo "Reading commands from $commands_file..."
sed -i 's/\r$//' "${sf_path}/masks/rfi-commands.txt"

# Loop through each command in the commands_file
i=0
while IFS= read -r command || [ -n "$command" ]; do
    # Skip empty lines
    [[ -z "$command" ]] && continue
    
    sbatch_script="${sbatch_path}/rfi_job_${i}.sbatch"

    echo "#!/bin/bash" > "$sbatch_script"
    echo "#SBATCH --job-name=rfifind_$i" >> "$sbatch_script"
    echo "#SBATCH --output=$sf_path/masks/sbatch_scripts/rfi_$i.out" >> "$sbatch_script"
    echo "#SBATCH --error=$sf_path/masks/sbatch_scripts/rfi_$i.err" >> "$sbatch_script"
    echo "#SBATCH --time=10:00:00" >> "$sbatch_script"
    echo "#SBATCH --mem=300G" >> "$sbatch_script"
    echo "#SBATCH --ntasks=1" >> "$sbatch_script"
    echo "#SBATCH --mail-type=END" >> "$sbatch_script"
    echo "#SBATCH --mail-user=ojohnson@tcd.ie" >> "$sbatch_script"
    echo "" >> "$sbatch_script"

    # Add the specific command to the sbatch script
    echo "cd /fred/oz203/data/PX094/J0523-2529/merged_sf" >> "$sbatch_script"
    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"
    echo "$command" >> "$sbatch_script"
    echo "" >> "$sbatch_script"

    sbatch "$sbatch_script"
    i=$((i + 1))
done < "$commands_file"

echo "Generated $i sbatch scripts."