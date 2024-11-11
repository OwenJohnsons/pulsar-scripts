export PSRHOME="/apps/users/pulsar/skylake/gcc-11.3.0/software/psrchive/4c0597b7b/bin/"
export LD_LIBRARY_PATH=/fred/oz002/psrhome/opt/cfitsio/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/fred/oz002/psrhome/opt/fftw-3.2.2-double/lib:/fred/oz002/psrhome/opt/fftw-3.2.2/lib:$LD_LIBRARY_PATH

# 1: file to split
file=$1
cd $(dirname $file)
echo "working directory: $(pwd)"

# split the file into three parts
base_name=$(basename $file) # remove extension
output_name=${base_name%.*}
# echo "output names: ${output_name}_[0.7,1.9GHz].sf, ${output_name}_[1.9,3.0GHz].sf, ${output_name}_[3.0,4.0GHz].sf"

pfitsUtil_searchmode_extractFreq -f $file -o frequency_split/${output_name}_0.7-1.9GHz.sf -c1 0 -c2 4607
pfitsUtil_searchmode_extractFreq -f $file -o frequency_split/${output_name}_1.9-3.0GHz.sf -c1 4608 -c2 9215
pfitsUtil_searchmode_extractFreq -f $file -o frequency_split/${output_name}_3.0-4.0GHz.sf -c1 9216 -c2 13311