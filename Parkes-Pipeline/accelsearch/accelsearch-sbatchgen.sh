#!/bin/bash

path=$1

for folder in $path/uwl*; do 
    count=0
    batch_number=1
    fft_files=()  # Array to store FFT files in batches of 20

    # Make directory for accelsearch
    mkdir -p $folder/prepdata/accelsearch

    # Define the sbatch file name
    sbatch_file=$folder/prepdata/accelsearch/accelsearch_${batch_number}.sbatch

    # Function to initialize a new sbatch file
    initialize_sbatch_file() {
        echo "#!/bin/bash" > $1
        echo "#SBATCH --job-name=accelsearch" >> $1
        echo "#SBATCH --output=$folder/prepdata/accelsearch/accelsearch_${batch_number}.out" >> $1
        echo "#SBATCH --output=$folder/prepdata/accelsearch/accelsearch_${batch_number}.out"
        echo "#SBATCH --error=$folder/prepdata/accelsearch/accelsearch_${batch_number}.err" >> $1
        echo "#SBATCH --time=05:30:00" >> $1
        echo "#SBATCH --mem=2GB" >> $1  
        echo "#SBATCH --cpus-per-task=6" >> $1
        echo "export OMP_NUM_THREADS=6" >> $1
        echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> $1
    }

    # Initialize the first sbatch file
    initialize_sbatch_file $sbatch_file

    # Loop through files and add them to the array
    for file in $(find "$folder" -name "*_red.fft"); do
        accel_pattern="${file%.fft}_ACCEL_*"
        accel_dir=$(dirname "$file")

        # Check for files matching the pattern with no extensions
        base_files=$(find "$accel_dir" -type f -name "$(basename "$accel_pattern")" ! -name "*.txtcand" ! -name "*.cand")

        if [[ -n "$base_files" ]]; then
            # If a file without extension exists, skip processing
            # echo "Skipping $file as a no-extension ACCEL file exists."
            continue
        fi
            fft_files+=("$file")
        count=$((count + 1))

        if [ $count -eq 20 ]; then
            # Write fft_files array to the sbatch file
            echo "fft_files=(" >> $sbatch_file
            for fft_file in "${fft_files[@]}"; do
                echo "    \"$fft_file\"" >> $sbatch_file
            done
            echo ")" >> $sbatch_file

            echo "parallel -j 2 bash ~/pulsar-scripts/Parkes-Pipeline/accelsearch/accelsearch-single.sh {} 4 ::: \"\${fft_files[@]}\"" >> $sbatch_file

            # Submit the sbatch file
            sbatch $sbatch_file

            # Reset count and fft_files, and increment batch number
            count=0
            fft_files=()
            batch_number=$((batch_number + 1))

            # Create a new sbatch file
            sbatch_file=$folder/prepdata/accelsearch/accelsearch_${batch_number}.sbatch
            initialize_sbatch_file $sbatch_file
        fi
    done

    # Handle any remaining files after the loop
    if [ $count -gt 0 ]; then
        echo "fft_files=(" >> $sbatch_file
        for fft_file in "${fft_files[@]}"; do
            echo "    \"$fft_file\"" >> $sbatch_file
        done
        echo ")" >> $sbatch_file
        echo "parallel -j 2 bash ~/pulsar-scripts/Parkes-Pipeline/accelsearch/accelsearch-single.sh {} 4 ::: \"\${fft_files[@]}\"" >> $sbatch_file

        sbatch $sbatch_file
    fi

done
