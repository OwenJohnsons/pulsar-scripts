path=$1

for folder in $path/uwl*; do 
    count=0
    batch_number=1

    # Make directory for accelsearch
    mkdir -p $folder/prepdata/accelsearch

    # Define the sbatch file name
    sbatch_file=$folder/prepdata/accelsearch/accelsearch_${batch_number}.sbatch

    # Function to initialize a new sbatch file
    initialize_sbatch_file() {
        echo "#!/bin/bash" > $1
        echo "#SBATCH --job-name=accelsearch" >> $1
        echo "#SBATCH --output=$folder/prepdata/accelsearch/accelsearch_${batch_number}.out" >> $1
        echo "#SBATCH --error=$folder/prepdata/accelsearch/accelsearch_${batch_number}.err" >> $1
        echo "#SBATCH --time=05:00:00" >> $1
        echo "#SBATCH --mem=2GB" >> $1  
        echo "#SBATCH --cpus-per-task=16" >> $1
        echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> $1
    }

  
    initialize_sbatch_file $sbatch_file

    # Loop through files and add commands
    for file in $(find "$folder" -name "*_red.fft"); do
        count=$((count + 1))
        echo "bash ~/pulsar-scripts/Parkes-Pipeline/accelsearch/accelsearch-single.sh $file" >> $sbatch_file
        
        if [ $count -eq 10 ]; then
            # Submit the sbatch file
            sbatch $sbatch_file

            # Reset count and increment batch number
            count=0
            batch_number=$((batch_number + 1))

            # Create a new sbatch file
            sbatch_file=$folder/prepdata/accelsearch/accelsearch_${batch_number}.sbatch
            initialize_sbatch_file $sbatch_file
        fi
    done
done
