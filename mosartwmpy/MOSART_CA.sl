#!/usr/bin/env /bin/bash
#SBATCH --partition=slurm
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --account=GODEEEP
#SBATCH --time=96:00:00
#SBATCH --job-name=mosartwmpy

echo 'Loading modules'

module purge
module load python/miniconda3.9
source /share/apps/python/miniconda3.9/etc/profile.d/conda.sh
conda activate mosartwmpypip

echo 'Done loading modules'

ulimit -s unlimited

python -u MOSART_CA.py

echo 'Really Done'