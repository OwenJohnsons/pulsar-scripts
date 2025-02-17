#!/bin/bash
path=$1

# Check if mask directory exists in path
if [ ! -d "${path}/masks" ]; then
    echo "Creating masks directory in ${path}..."
    mkdir "${path}/masks"
fi

# Check if logs directory exists in path
if [ ! -d "${path}/masks/logs" ]; then
    echo "Creating logs directory in ${path}/masks..."
    mkdir "${path}/masks/logs"
fi

echo "Finding .sf files in ${path}..."

find "${path}" -type f -name "*.sf" | while read -r filename; do
    # Extract the base name of the file (without the directory path and extension)
    base_name=$(basename "$filename" .sf)
    folder_path=$(dirname "$filename")   

    # Check if .mask file already exists
    if [ -e "${folder_path}/masks/${base_name}_rfifind.mask" ]; then
        echo "Mask file already exists for ${base_name}, skipping rfifind..."
    else
 
        sbatch_script="${folder_path}/masks/${base_name}_rfifind.sbatch"
        echo "Generating sbatch: ${sbatch_script}..."

        # Create sbatch script
        echo "#!/bin/bash" > "$sbatch_script"
        echo "#SBATCH --job-name=rfifind" >> "$sbatch_script"
        echo "#SBATCH --output=${folder_path}/masks/${base_name}_rfifind.out" >> "$sbatch_script"
        echo "#SBATCH --error=${folder_path}/masks/${base_name}_rfifind.err" >> "$sbatch_script"
        echo "#SBATCH --time=05:00:00" >> "$sbatch_script"
        echo "#SBATCH --mem=12G" >> "$sbatch_script"
        echo "#SBATCH --ntasks=4" >> "$sbatch_script"
        echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"

        echo "cd "${folder_path}/masks"" >> "$sbatch_script"
        
        if [[ "$base_name" == *"0.7-1.9GHz"* ]]; then
            echo "rfifind -time 10 -ncpus 4 -noclip -freqsig 6 -timesig 6 -chanfrac 0.4 -intfrac 0.4 -zapchan 0:115,216:335,402,485:563,575,578,582,664:743,778:809,812:895,958:991,996:1024,1252:1259,1276:1283,1292,1296,1300:1307,1316,1348,1432,1456,1472,1501:1504,1508,1511:1530,1596,1600,1668,1724,1735:1737,1784,1788,2084:2103,2784,3176:3179,3183:3184,3656:3689,4024:4128,4164:4203,4404:4483,4564:4607 -o \"${base_name}\" \"$filename\"" >> "$sbatch_script"
        elif [[ "$base_name" == *"1.9-3.0GHz"* ]]; then
            echo "rfifind -time 10 -ncpus 4 -noclip -freqsig 8 -timesig 8 -chanfrac 0.6 -intfrac 0.6 -zapchan 0:35,96:191,256,471:539,704:707,828:831,884:887,892:895,948:951,1016:1055,1076:1095,1136:1195,1216:1219,1236:1255,1340:1343,1396:1399,1404:1407,1460:1463,1481:1482,1784:2103,2524:2559,2776:2855,3256:3335 -o \"${base_name}\" \"$filename\"" >> "$sbatch_script"
        elif [[ "$base_name" == *"3.0-4.0GHz"* ]]; then
            echo "rfifind -time 10 -ncpus 4 -noclip -freqsig 10 -timesig 10 -chanfrac 0.8 -intfrac 0.8 -zapchan 0,1493:1571,1913:1991 -o \"${base_name}\" \"$filename\"" >> "$sbatch_script"
        else
            echo "Slice not found for $base_name"
        fi
        
        # Submit the job
        sbatch "$sbatch_script"
        # break 
    fi
done
