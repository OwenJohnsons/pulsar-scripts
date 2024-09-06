#!/bin/bash
#!/bin/bash
#SBATCH --job-name=addsearch
#SBATCH --output=addsearch_%j.out
#SBATCH --error=addsearch_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=24:00:00
#SBATCH --mem=300G

source /fred/oz002/psrhome/scripts/psrhome.sh
bash addsearch-run.sh /fred/oz203/data/PX094/J0523-2529/2022OCTS09/raw/run1 16 