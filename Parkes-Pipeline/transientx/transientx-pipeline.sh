#!/bin/bash

path=$1

files=$(find "$path" -name "*.sf" -print)
echo "Number of .sf files found:" $(echo "$files" | wc -l)

for file in $files; do
    basename=$(basename "$file" .sf)
    basepath=$(dirname "$file")
    
    # Check if the mask file exists
    mask="${basepath}/masks/${basename}_rfifind.mask"
    echo "${basename}" 

    if [ -e "$mask" ]; then
        sbatch_script="${basepath}/${basename}_transientx.sbatch"
        output_directory="$./transientx"

        if [[ "$basename" == *"0.7-1.9GHz"* ]]; then
            transx_command="transientx_fil -v --psrfits --thre 7 --dms 0 --ddm 0.1 --overlap 0.1 --ndm 600 -l 30 -o ${output_directory}/${basename} --minw 3e-5 --maxw 0.3 -z ${mask} zdot -f ${file}"
        
        elif [[ "$basename" == *"1.9-3.0GHz"* ]]; then
            transx_command="transientx_fil -v --psrfits --thre 7 --dms 0 --ddm 0.5 --overlap 0.1 --ndm 150 -l 30 -o ${output_directory}/${basename} --minw 3e-5 --maxw 0.3 -z ${mask} zdot -f ${file}"

        elif [[ "$basename" == *"3.0-4.0GHz"* ]]; then
            transx_command="transientx_fil -v --psrfits --thre 7 --dms 0 --ddm 1 --overlap 0.1 --ndm 60 -l 30 -o ${output_directory}/${basename} --minw 3e-5 --maxw 0.3 -z ${mask} zdot -f ${file}"

        #sbatch preamble 
        echo "#!/bin/bash" > "$sbatch_script"
        echo "#SBATCH --job-name=transientx" >> "$sbatch_script"
        echo "#SBATCH --output=${output_directory}/${basename}_transientx.out" >> "$sbatch_script"
        echo "#SBATCH --error=${output_directory}/${basename}_transientx.err" >> "$sbatch_script"
        echo "#SBATCH --time=05:00:00" >> "$sbatch_script"
        echo "#SBATCH --mem=12G" >> "$sbatch_script"
        echo "#SBATCH --ntasks=4" >> "$sbatch_script"
        echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"

        echo "cd ${output_directory}" >> "$sbatch_script" 
        echo "[ -d ./transientx ] || mkdir ./transientx" >> "$sbatch_script"
        echo "${transx_command}" >> "$sbatch_script"

        # sbatch "$sbatch_script"
done 