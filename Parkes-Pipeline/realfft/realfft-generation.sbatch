path=$1

folders=$(ls -d $path/uwl*) 

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

    # sbatch generation

    echo "sbatch generation for folder: " $folder

    # sbatch_file=$folder/realfft-generation.sbatch
    # echo "sbatch file: " $sbatch_file
    
    # echo "#!/bin/bash" >> "$sbatch_script"
    # echo "#SBATCH --job-name=realfft-generation" >> "$sbatch_script"
    # echo "#SBATCH --output=$folder/realfft-generation.out" >> "$sbatch_script"
    # echo "#SBATCH --error=$folder/realfft-generation.err" >> "$sbatch_script"
    # echo "#SBATCH --time=00:30:00" >> "$sbatch_script"
    # echo "bash ~/pulsar-scripts/Parkes-Pipeline/realfft/realfft-job.sh $folder" >> "$sbatch_script"

    # sbatch "$sbatch_script"
done 