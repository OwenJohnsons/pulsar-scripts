
path=$1

# Find all folders in the given path
folders=$(find "$path" -type d)

for folder in $folders; do
    # bash rfi-command-generator.sh "$folder"
    bash rfi-sbatchjob-generator.sh "$folder"
done