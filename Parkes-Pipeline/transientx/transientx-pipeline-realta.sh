#!/bin/bash

path=$1

files=$(find "$path" -name "*.fil" -print)
echo "Number of .sf files found:" $(echo "$files" | wc -l)

# Kadane Parameters
downsamp=3
snrthresh=6
#-z kadaneF 6 3 kadaneT 6 3

for file in $files; do
    basename=$(basename "$file" .sf)
    basepath=$(dirname "$file")
    
    # Check if the mask file exists
    mask="${basepath}/*.mask"
    cd $basepath
    file="${basename}.fil"

    output_directory="transientx_output"
    if [ ! -d "$output_directory" ]; then
        mkdir "$output_directory"
    fi

    if [ -e "$mask" ]; then
        transientx_fil -v --psrfits -l 10 --ddm 0.05 --overlap 0.1 --ndm 2000 --minw 0.00003 --maxw 0.005 -z ${mask} zdot -o ${output_directory}/${basename} -f ${file}

    else     
        echo "Mask file not found for ${basename}"
        echo "Generating mask file for ${basename}"

        rfi_command="rfifind -time 30 -timesig 8 -freqsig 4 -chanfrac 0.4 -intfrac 0.6 -o \"${basename}\" \"${file}\""
        docker run -it --rm --gpus all --network=host --env DISPLAY=$DISPLAY \
            -v "$PWD":"$PWD" -w "$PWD" clfd-psrchive-python3.6 \
            /bin/bash -c "${rfi_command}"

        mask="${basepath}/*.mask"
        transientx_fil -v --psrfits -l 10 --ddm 0.05 --overlap 0.1 --ndm 2000 --minw 0.00003 --maxw 0.005 -z ${mask} zdot -o ${output_directory}/${basename} -f ${file}

    fi  
done 
