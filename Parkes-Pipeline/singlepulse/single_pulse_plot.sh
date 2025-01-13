path=$1

for folder in $(ls -d ${path}/uwl*/prepdata/*Hz); do
    single_pulse_search.py "$folder/*.singlepulse"
    # convert ps to jpg
    ps_file=$(ls $folder/*.singlepulse.ps)
    jpg_file=$(echo $ps_file | sed 's/.ps/.jpg/')
    convert -density 300 $ps_file $jpg_file
    cp $jpg_file /fred/oz203/data/PX094/J0523-2529/cand_plot/singlepulse
done 