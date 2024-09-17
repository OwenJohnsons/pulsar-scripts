dir="./"

# Loop through each .ps file in the directory
for file in "$dir"*.ps; do
    if [ -f "$file" ]; then
        # Convert .ps to .jpg
        convert -density 300 -rotate 90 "$file" "${file%.ps}.jpg"
        echo "Converted $file to ${file%.ps}.jpg"
    fi
done

echo "Conversion completed."