#!/usr/bin/env /bin/bash

#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --account=GODEEEP
#SBATCH --time=48:00:00
#SBATCH --array=0-40

echo 'Loading modules'

module load python/miniconda3.9
source /share/apps/python/miniconda3.9/etc/profile.d/conda.sh
conda activate vic

module load gcc/11.2.0
module load intel/20.0.4
module load netcdf/4.8.0
module load openmpi/4.1.0
module load intelmpi/2020u4
module load cdo

echo 'Done loading modules'

start_year=1979
end_year=2019
for ((year = start_year; year <= end_year; year++))
do
  years+=($year)
done

srun python -u runoff-subset-by-huc2.py ${years[SLURM_ARRAY_TASK_ID]}

echo 'Really Done'
