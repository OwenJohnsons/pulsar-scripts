#!/bin/bash

path=$1 
cd $path || { echo "Directory not found: $path"; exit 1; }
path=$(pwd)

output_rootdir="/lorule/scratch/oaj00001/data" 
fits_files=$(find "$path" -name "*.fits")
prefixes=()

for file in $fits_files; do
    base=$(basename "$file" .fits)
    prefix=${base%_[0-9][0-9][0-9][0-9]}
    prefixes+=("$prefix")
done

unique_prefixes=($(printf "%s\n" "${prefixes[@]}" | sort -u))
printf "%s\n" "${unique_prefixes[@]}"

for prefix in "${unique_prefixes[@]}"; do
    if [ -f "$path/${prefix}_rfifind.mask" ]; then 

        output_dir="$output_rootdir/$prefix"
        rfifind_mask="$path/${prefix}_rfifind.mask"

        if [ ! -d "$output_dir/prepsub" ]; then
            mkdir -p "$output_dir/prepsub"
            echo "Created directory: $output_dir/prepsub"
        fi
        prepdata_command="prepsubband -nsub 128 -dmstep 0.1 -numdms 600 -o ${output_dir}/prepsub/${prefix} -mask $rfifind_mask ${path}/${prefix}_*.fits"
        sbatch_script="${output_dir}/${prefix}_prepdata.sbatch"

        echo "#!/bin/bash" > "$sbatch_script"
        echo "#SBATCH --job-name=prepdata" >> "$sbatch_script"
        echo "#SBATCH --output=${output_dir}/${prefix}_prepdata.out" >> "$sbatch_script"
        echo "#SBATCH --error=${output_dir}/${prefix}_prepdata.err" >> "$sbatch_script"
        echo "#SBATCH --time=05:00:00" >> "$sbatch_script"
        echo "#SBATCH --mem=1G" >> "$sbatch_script"
        echo "#SBATCH --ntasks=1" >> "$sbatch_script"

        echo "${prepdata_command}" >> "$sbatch_script"
        echo "Running: $sbatch_script"
        sbatch "$sbatch_script"

    else
        echo "${prefix}_rfifind.mask not found"
        continue
    fi
done