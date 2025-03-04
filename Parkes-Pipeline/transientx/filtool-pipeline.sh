#!/bin/bash

prefix=$1
path=$2

for file in $(find "${path}" -name "*${prefix}*.sf" -print); do
    basename=$(basename "$file" .sf)
    basepath=$(dirname "$file")
    filname="${basepath}/${basename}_01.fil"
    mask="${basepath}/masks/${basename}_rfifind.mask"

    #SBATCH Command 
    sbatch_file="${basepath}/${basename}_filgen.sbatch"
    echo "Creating sbatch file: $sbatch_file"
    echo "#!/bin/bash" > $sbatch_file
    echo "#SBATCH --job-name=${basename}_filgen" >> $sbatch_file
    echo "#SBATCH --output=${basepath}/${basename}_filgen.out" >> $sbatch_file
    echo "#SBATCH --error=${basepath}/${basename}_filgen.err" >> $sbatch_file
    echo "#SBATCH --time=4:00:00" >> $sbatch_file
    echo "#SBATCH --mem=6G" >> $sbatch_file

    echo "cd ${basepath}" >> $sbatch_file

    if [ ! -f "$filname" ]; then
        file="${basename}.sf"
        filtool_command="filtool -v --psrfits --nbits 2 --mean 1.5 --std 1 -z zdot -o ${basename} ${file}"
        echo "apptainer exec --pwd \$(pwd) --bind ${basepath}:/mnt ~/pulsarx_uwl.sif /bin/bash -c '${filtool_command}'" >> "$sbatch_file"
    fi

    filterbank="${basename}_01.fil"

    if [[ "$basename" == *"0.7-1.9GHz"* ]]; then
        echo "rfifind -time 10 -ncpus 4 -zapchan 0:115,216:335,402,485:563,575,578,582,664:743,778:809,812:895,958:991,996:1024,1252:1259,1276:1283,1292,1296,1300:1307,1316,1348,1432,1456,1472,1501:1504,1508,1511:1530,1596,1600,1668,1724,1735:1737,1784,1788,2084:2103,2784,3176:3179,3183:3184,3656:3689,4024:4128,4164:4203,4404:4483,4564:4607 -o masks/${basename} $filterbank" >> "$sbatch_file"
    elif [[ "$basename" == *"1.9-3.0GHz"* ]]; then
        echo "rfifind -time 10 -ncpus 4 -zapchan 0:35,96:191,256,471:539,704:707,828:831,884:887,892:895,948:951,1016:1055,1076:1095,1136:1195,1216:1219,1236:1255,1340:1343,1396:1399,1404:1407,1460:1463,1481:1482,1784:2103,2524:2559,2776:2855,3256:3335 -o masks/${basename} $filterbank" >> "$sbatch_file"
    elif [[ "$basename" == *"3.0-4.0GHz"* ]]; then
        echo "rfifind -time 10 -ncpus 4 -zapchan 0,1493:1571,1913:1991 -o masks/${basename} $filterbank" >> "$sbatch_file"
    else
        echo "Slice not found for $basename"
    fi

    if [[ "$basename" == *"0.7-1.9GHz"* ]]; then
        echo "prepsubband -nsub 64 -lodm 0 -dmstep 0.1 -numdms 1 -ignorechan 0:115,216:335,402,485:563,575,578,582,664:743,778:809,812:895,958:991,996:1024,1252:1259,1276:1283,1292,1296,1300:1307,1316,1348,1432,1456,1472,1501:1504,1508,1511:1530,1596,1600,1668,1724,1735:1737,1784,1788,2084:2103,2784,3176:3179,3183:3184,3656:3689,4024:4128,4164:4203,4404:4483,4564:4607 -mask $mask -o ${basename}_rfitest ${basename}_01.fil" >> "$sbatch_file"
    elif [[ "$basename" == *"1.9-3.0GHz"* ]]; then
        echo "prepsubband -nsub 64 -lodm 0 -dmstep 0.5 -numdms 1 -ignorechan 0:35,96:191,256,471:539,704:707,828:831,884:887,892:895,948:951,1016:1055,1076:1095,1136:1195,1216:1219,1236:1255,1340:1343,1396:1399,1404:1407,1460:1463,1481:1482,1784:2103,2524:2559,2776:2855,3256:3335 -mask $mask -o ${basename}_rfitest ${basename}_01.fil" >> "$sbatch_file"
    elif [[ "$basename" == *"3.0-4.0GHz"* ]]; then
        echo "prepsubband -nsub 64 -lodm 0 -dmstep 1 -numdms 1 -ignorechan 0,1493:1571,1913:1991 -mask $mask -o ${basename}_rfitest ${basename}_01.fil" >> "$sbatch_file"
    else
        echo "Slice not found for $basename"
    fi

    sbatch $sbatch_file
done
