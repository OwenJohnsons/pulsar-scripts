path=$1

for folder in $(ls -d ${path}/uwl*/prepdata/*Hz); do

    # echo "Processing $folder"
    
    sbatch_script="$folder/single_pulse.sbatch"
    echo $folder

    echo "#!/bin/bash" > "$sbatch_script"
    echo "#SBATCH --job-name=single_pulse" >> "$sbatch_script"
    echo "#SBATCH --output=$folder/single_pulse.out" >> "$sbatch_script"
    echo "#SBATCH --error=$folder/single_pulse.err" >> "$sbatch_script"
    echo "#SBATCH --time=01:00:00" >> "$sbatch_script"
    echo "#SBATCH --mem=1G" >> "$sbatch_script"

    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"
    echo "cd $folder" >> "$sbatch_script"
    echo "bash ~/pulsar-scripts/Parkes-Pipeline/singlepulse/single_pulse.sh ./" >> "$sbatch_script"

    sbatch "$sbatch_script"
done 