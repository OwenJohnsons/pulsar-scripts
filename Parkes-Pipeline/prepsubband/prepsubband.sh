#!/bin/bash

# Code Purpose: Find all .sf files in a given directory and create sbatch jobs to prepsubband.
# Input: The path to the directory containing the .sf files.

path=$1

# Find all .sf files in the given path
files=$(find "$path" -name "*.sf" -print)
echo "Number of .sf files found:" $(echo "$files" | wc -l)

for file in $files; do
    basename=$(basename "$file" .sf)
    basepath=$(dirname "$file")
    
    # Check if the mask file exists
    mask="${basepath}/masks/${basename}_rfifind.mask"
    prepdatafile="${basepath}/prepdata/${basename}_prepdata.dat"
    if [ -e "$mask" ]; then
            
            # make prepdata directory if it doesn't exist
            mkdir -p "${basepath}/prepdata"
            mkdir -p "${basepath}/prepdata/logs"
            mkdir -p "${basepath}/prepdata/sbatch_scripts"
    
            # create sbatch script
            # overwrite the sbatch script if it already exists

            sbatch_script="${basepath}/prepdata/sbatch_scripts/${basename}_prepdata.sbatch"
            echo "#!/bin/bash" > "$sbatch_script"
            echo "#SBATCH --job-name=prepdata" >> "$sbatch_script"
            echo "#SBATCH --output=${basepath}/prepdata/logs/${basename}_prepdata.out" >> "$sbatch_script"
            echo "#SBATCH --error=${basepath}/prepdata/logs/${basename}_prepdata.err" >> "$sbatch_script"
            echo "#SBATCH --time=1-00:00:00" >> "$sbatch_script"
            echo "#SBATCH --mem=1G" >> "$sbatch_script"
            echo "#SBATCH --ntasks=1" >> "$sbatch_script"
            echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"

            echo "cd $basepath" >> "$sbatch_script"
            
            # Determine which slice is being ingested, 0.7-1.9GHz.sf, 1.9-3.0GHz.sf or 3.0-4.0GHz.sf
            if [[ "$basename" == *"0.7-1.9GHz"* ]]; then
                echo "prepsubband -nsub 64 -lodm 0 -dmstep 0.1 -numdms 600 -ignorechan 0:115,216:335,402,485:563,575,578,582,664:743,778:809,812:895,958:991,996:1024,1252:1259,1276:1283,1292,1296,1300:1307,1316,1348,1432,1456,1472,1501:1504,1508,1511:1530,1596,1600,1668,1724,1735:1737,1784,1788,2084:2103,2784,3176:3179,3183:3184,3656:3689,4024:4128,4164:4203,4404:4483,4564:4607 -mask $mask -o ./prepdata/${basename}_prepsub $basename.sf" >> "$sbatch_script"
                echo "mv ${basepath}/prepdata/${basename}_prepsub* ${basepath}/prepdata/0.7-1.9GHz" >> "$sbatch_script"
            elif [[ "$basename" == *"1.9-3.0GHz"* ]]; then
                echo "prepsubband -nsub 64 -lodm 0 -dmstep 0.5 -numdms 150 -ignorechan 0:35,96:191,256,471:539,704:707,828:831,884:887,892:895,948:951,1016:1055,1076:1095,1136:1195,1216:1219,1236:1255,1340:1343,1396:1399,1404:1407,1460:1463,1481:1482,1784:2103,2524:2559,2776:2855,3256:3335 -mask $mask -o ./prepdata/${basename}_prepsub $basename.sf" >> "$sbatch_script"
                echo "mv ${basepath}/prepdata/${basename}_prepsub* ${basepath}/prepdata/1.9-3.0GHz" >> "$sbatch_script"
            elif [[ "$basename" == *"3.0-4.0GHz"* ]]; then
                echo "prepsubband -nsub 64 -lodm 0 -dmstep 1 -numdms 60 -ignorechan 0,1493:1571,1913:1991 -mask $mask -o ./prepdata/${basename}_prepsub $basename.sf" >> "$sbatch_script"
                echo "mv ${basepath}/prepdata/${basename}_prepsub* ${basepath}/prepdata/3.0-4.0GHz" >> "$sbatch_script"
            else
                echo "Slice not found for $basename"
            fi


        else
            if [ ! -e "$mask" ]; then
                echo "Mask file not found for $basename"
            fi
    
            if [ -e "$prepdatafile" ]; then
                echo "Prepdata file at 0 DM found for $basename"
            fi
        fi
done

# Run the sbatch scripts
for file in $files; do
    basename=$(basename "$file" .sf)
    basepath=$(dirname "$file")
    sbatch_script="${basepath}/prepdata/sbatch_scripts/${basename}_prepdata.sbatch"
    sbatch "$sbatch_script"
done