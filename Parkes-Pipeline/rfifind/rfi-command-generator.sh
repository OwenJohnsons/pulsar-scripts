#!/bin/bash
path=$1

# Check if mask directory exists in path
if [ ! -d "${path}/masks" ]; then
    echo "Creating masks directory in ${path}..."
    mkdir "${path}/masks"
fi

# clear .txt file if previous commands exist
echo > $path/masks/rfi-commands.txt

echo "Finding .sf files in ${path}..."

for filename in ${path}/*/*.sf; do
    # Extract the base name of the file (without the directory path and extension)
    base_name=$(basename "$filename" .sf)
    echo "Generating rfi command for ${base_name}..."
    
    # Check if .mask file already exists
    if [ -e "${path}/masks/${base_name}_rfifind.mask" ]; then
        echo "Mask file already exists for ${base_name}, skipping rfifind..."
    else
        # print the command to the output file
        echo rfifind -time 10 -ncpus 4 -noclip -freqsig 8 -timesig 8 -chanfrac 0.6 -intfrac 0.6 -zapchan 0:115,216:335,402,485:563,575,578,582,664:743,778:809,812:895,958:991,996:1024,1252:1259,1276:1283,1292,1296,1300:1307,1316,1348,1432,1456,1472,1501:1504,1508,1511:1530,1596,1600,1668,1724,1735:1737,1784,1788,2084:2103,2784,3176:3179,3183:3184,3656:3689,4024:4128,4164:4203,4404:4483,4564:4643,4704:4799,4864,5079:5147,5312:5315,5436:5439,5492:5495,5500:5503,5556:5559,5624:5663,5684:5703,5744:5803,5824:5827,5844:5863,5948:5951,6004:6007,6012:6015,6068:6071,6089:6090,6392:6711,7132:7167,7384:7463,7864:7943,9471,10964:11042,11384:11462 -o "${path}/masks/${base_name}" "$filename" >> $path/masks/rfi-commands.txt
    fi
done