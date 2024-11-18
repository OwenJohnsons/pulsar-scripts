path=$1

find "$path" -type d -name "*Hz*" | while read -r folder; do
    
    sbatch_script="$folder/single_pulse.sbatch"
    echo "#!/bin/bash" > "$sbatch_script"
    echo "#SBATCH --job-name=single_pulse" >> "$sbatch_script"
    echo "#SBATCH --output=$folder/single_pulse.out" >> "$sbatch_script"
    echo "#SBATCH --error=$folder/single_pulse.err" >> "$sbatch_script"
    echo "#SBATCH --time=10:00:00" >> "$sbatch_script"
    echo "#SBATCH --mem=2G" >> "$sbatch_script"

    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"
    echo "~/pulsar-scripts/Parkes-Pipeline/singlepulse/single_pulse.sh $folder" >> "$sbatch_script"

    # sbatch "$sbatch_script"
done 