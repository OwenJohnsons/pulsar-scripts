#path="/fred/oz203/data/PX094/J0523-2529/frequency_split"; for folder in ${path}/uwl*/prepdata/*Hz; do bash single_pulse.sh "$folder"; done
path=$1

for fft_file in $path/*_red.fft; do 
    # generate .dat 
    realfft $fft_file
done 

single_pulse_search.py -t 7 $path/*_red.dat
# rm $path/*_red.dat