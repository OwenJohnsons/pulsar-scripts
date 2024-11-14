path=$1

for folder in $path/uwl*; do 

    # make directory for accelsearch
    mkdir -p $folder/prepdata/accelsearch

    sbatch_file=$folder/prepdata/accelsearch/accelsearch.sbatch

    # overwrite the sbatch file
    echo "#!/bin/bash" > $sbatch_file
    echo "#SBATCH --job-name=accelsearch" >> $sbatch_file
    echo "#SBATCH --output=$folder/prepdata/accelsearch/accelsearch.out" >> $sbatch_file
    echo "#SBATCH --error=$folder/prepdata/accelsearch/accelsearch.err" >> $sbatch_file
    echo "#SBATCH --time=24:00:00" >> $sbatch_file
    echo "#SBATCH --mem=300GB" >> $sbatch_file
    echo "#SBATCH --cpus-per-task=16" >> $sbatch_file

    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> $sbatch_file
    echo "bash ~/pulsar-scripts/Parkes-Pipeline/accelsearch/accelsearch.sh $folder/prepdata" >> $sbatch_file


    # submit the sbatch file
    sbatch $sbatch_file
done 