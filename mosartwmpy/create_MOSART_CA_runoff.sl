#!/usr/bin/env /bin/bash
#SBATCH --partition=smp7 ### a partition on constance
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --account=GODEEEP
#SBATCH --time=96:00:00
#SBATCH --job-name=mosartwmpy_runoff

echo 'Loading modules'

module purge
module load python/miniconda3.9
source /share/apps/python/miniconda3.9/etc/profile.d/conda.sh
conda activate vic

echo 'Done loading modules'

ulimit -s unlimited

python -u create_MOSART_CA_runoff.py

echo 'Really Done'