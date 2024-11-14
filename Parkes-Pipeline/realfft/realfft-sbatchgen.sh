path=$1

folders=$(find "$path" -type d -name "uwl*" | sort)

if [ -z "$path" ]; then
    echo "Error: Path not provided or invalid"
    exit 1
fi

folders=$(ls -d $path/uwl* 2>/dev/null)
if [ -z "$folders" ]; then
    echo "Error: No matching folders found in $path"
    exit 1
fi

echo "Number of folders: " $(echo $folders | wc -w)

for folder in $folders; do  

    if [ -e "$sbatch_script" ]; then
        rm "$sbatch_script"
    fi

    if [ ! -d "$folder/prepdata/realfft" ]; then
        mkdir -p "$folder/prepdata/realfft"
    fi

    # SBATCH generation

    basename=$(basename $folder)
    # echo "Basename: $basename"
    sbatch_script="$folder/prepdata/realfft/${basename}_realfft.sbatch"
    # echo "sbatch script: $sbatch_script"

    echo "#!/bin/bash" > "$sbatch_script"
    echo "#SBATCH --job-name=realfft" >> "$sbatch_script"
    echo "#SBATCH --output=$folder/prepdata/realfft/${basename}_realfft.out" >> "$sbatch_script"
    echo "#SBATCH --error=$folder/prepdata/realfft/${basename}_realfft.err" >> "$sbatch_script"
    echo "#SBATCH --time=02:00:00" >> "$sbatch_script"
    echo "#SBATCH --mem=1G" >> "$sbatch_script"

    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"
    echo "bash ~/pulsar-scripts/Parkes-Pipeline/realfft/realfft-job.sh ${path}${basename}/prepdata" >> "$sbatch_script"

    sbatch "$sbatch_script"


done 