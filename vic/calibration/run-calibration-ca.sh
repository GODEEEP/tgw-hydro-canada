#!/usr/bin/env /bin/bash

huc2="00"

csv_in=../input/grid_ids_ca_check.csv
path_out=/vast/projects/godeeep/VIC/calibration/$huc2 

points=($(tail -n +2 $csv_in | awk -F ',' '{print $2;}'))
total_points=${#points[@]}

start_id=$((SLURM_NODEID*total_points/total_nodes))
end_id=$((SLURM_NODEID*total_points/total_nodes+total_points/total_nodes-1))

if (( end_id >= total_points-1 )); then
  end_id=$((total_points-1))
fi

echo "NODE $SLURM_NODEID: points ${points[$start_id]} - ${points[$end_id]}"

export OMP_NUM_THREADS=1

~/bin/parallel --jobs 64 "python run-calibration-impi.py $csv_in $path_out " ::: "${points[@]:$start_id:$end_id-$start_id+1}"