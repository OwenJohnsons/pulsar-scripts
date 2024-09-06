# Code Purpose: Run addsearch to search together .sf files in a directory and output to a single .sf file
# Usage: bash addsearch-run.sh <directory>
# Input: Directory containing .sf files
# Output: Single .sf file containing merged files

path=$1
merge_factor=$2

# Check if directory exists
if [ ! -d "$path" ]; then
    echo "Directory does not exist"
    exit 1
fi

# Get the list of .sf files in the directory
files=($path/*.sf)
file_num=${#files[@]}

# sort by number i.e. 11, 12, 13 
IFS=$'\n' files=($(sort -V <<<"${files[*]}"))
unset IFS

echo "Number of .sf files in directory: $file_num"

# Check if the number of files is less than 34, less than a 2 hour run 
if [ $file_num -lt 34 ]; then
    echo "File count is less than 34, merging all files into a single .sf file"
    
    files_to_add=""
    for file in "${files[@]}"; do
        files_to_add+="$file "
    done
    
    /home/ojohnson/addsearch/addsearch -E add.sf $files_to_add
    
    # Move the result to addsearch directory one level up
    # mkdir -p $path/../addsearch
    # mv $path/*.add $path/../addsearch
    
    echo 'Number of .add files in current directory: ' $(ls $path | grep -c ".add")
    # echo "addsearch completed. Number of .add files in $path/../addsearch: $(ls $path/../addsearch | wc -l)"
else
    # Proceed with highest common factor logic
    # fct_num=$file_num
    # div_num=$(factor $fct_num | awk '{print $NF}')
    highest_factor=$merge_factor

    echo "Merging $highest_factor together" 

    # Run addsearch for highest common factor
    for ((i=0; i<file_num; i+=highest_factor)); do
        echo "Running addsearch for files from $i.sf to $((i + highest_factor - 1)).sf"
        
        files_to_add=""
        
        for ((j=i; j<i+highest_factor && j<file_num; j++)); do
            files_to_add+="${files[$j]} "
        done
        
        /home/ojohnson/addsearch/addsearch -E add.sf $files_to_add
    done

    # Move the result to addsearch directory one level up
    # mkdir -p $path../addsearch
    # mv $path/*.add $path../addsearch
    
    echo 'Number of .add files in current directory: ' $(ls $path | grep -c ".add")
fi