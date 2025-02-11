path=$1

for folder in $(ls -d ${path}/uwl*/prepdata/*4.0GHz); do

    # echo "Processing $folder"
    
    sbatch_script="$folder/single_pulse.sbatch"
    echo $sbatch_script

    echo "#!/bin/bash" > "$sbatch_script"
    echo "#SBATCH --job-name=single_pulse" >> "$sbatch_script"
    echo "#SBATCH --output=$folder/single_pulse.out" >> "$sbatch_script"
    echo "#SBATCH --error=$folder/single_pulse.err" >> "$sbatch_script"
    echo "#SBATCH --time=2:00:00" >> "$sbatch_script"
    echo "#SBATCH --mem=2G" >> "$sbatch_script"

    echo "source /fred/oz002/psrhome/scripts/psrhome.sh" >> "$sbatch_script"
    echo "cd $folder" >> "$sbatch_script"
    # echo "mkdir ./prepdata" >> "$sbatch_script"
    # echo 'for file in *.inf; do [[ "$file" == *_red.inf ]] && continue; cp "$file" "${file%.inf}_red.inf"; done' >> "$sbatch_script"
    # echo 'cp *_red.inf ./prepdata' >> "$sbatch_script"

    # echo "for file in *.dat; do realfft \$file; done" >> $sbatch_script 
    # echo "for file in *.fft; do [[ "\$file" == *_red.fft ]] || rednoise "\$file"; done" >> "$sbatch_script"
    # echo "for file in *_red.fft; do realfft \$file; done" >> $sbatch_script
    # echo "find . -maxdepth 1 -type f -name "*.dat" ! -name "*_red.dat" -delete" >> "$sbatch_script"
    # echo "find . -maxdepth 1 -type f -name "*.fft" ! -name "*_red.fft" -delete" >> "$sbatch_script" 
    # echo "single_pulse_search.py -t 0 *_red.dat" >> $sbatch_script
    echo "for file in *_red.dat; do single_pulse_search.py \$file; done" >> $sbatch_script
    echo "rm -r ./prepdata" >> "$sbatch_script"


    sbatch "$sbatch_script"
done 