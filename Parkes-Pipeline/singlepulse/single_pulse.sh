
path=$1

for fft_file in $path/*.fft; do 
    # generate .dat 
    realfft $fft_file
done 

single_pulse_search.py $path/*.dat
# remove .dat files
rm $path/*.dat
single_pulse_search.py $path/*.singlepulse

for ps_file in $path/*.ps; do
    echo $ps_file
    # convert .ps to .jpg
    convert -density 300 $ps_file ${ps_file%.ps}.jpg
    cp ${ps_file%.ps}.jpg "/fred/oz203/data/PX094/J0523-2529/cand_plot/singlepulse"

done