# tgw-hydro-canada
A collection of scripts to produce monthly hydropower generation estimates for 110 facilities in British Columbia and Alberta to support the Western-US Interconnect grid system studies. The dataset is published in the Zenodo repository and can be accessed at the following link: https://zenodo.org/record/14984725 (DOI: 10.5281/zenodo.14984725)."

---

## Model Used
- Variable Infiltration Capacity(VIC): https://vic.readthedocs.io/en/master/
- Optimization Software Toolkit for Research Involving Computational Heuristics (OSTRICH): https://www.eng.buffalo.edu/~lsmatott/Ostrich/OstrichMain.html
- Model for Scale Adaptive River Transport with Water Management(mosartwmpy): https://mosartwmpy.readthedocs.io/en/latest/
- Python Environment to Run Codes Below: [godeep_can.yaml](./godeeep_can.yaml)

For information on the computational resources and software dependencies of the VIC, OSTRICH, and mosartwmpy models, please refer to the technical manuals at the respective links above.

---

## Code Descriptions
  1. `vic/`: hydrologic modeling to generate runoff <br>
     * [vic/grid_ids_ca.py](./vic/grid_ids_ca.py): <br>
     create a list of VIC grids for Western Canada <br>
     
     * [vic/param-subset-by-huc2.py](./vic/param-subset-by-huc2.py): <br>
     extract VIC domain parameters on VIC grids from [VICGlobal](https://zenodo.org/record/5038653/) dataset <br>
     
     * [vic/proc_wrf_to_vicgrid_00625_parallel.py](./vic/proc_wrf_to_vicgrid_00625_parallel.py): <br>
     convert [TGW](https://tgw-data.msdlive.org/) historical climate run into weekely meteorological forcing data on VIC grids at 1/16th degree resolution <br>
     
     * [vic/conus-forcings-by-huc2-from-weekly.py](./vic/conus-forcings-by-huc2-from-weekly.py): <br>
     generate VIC meteorological forcing inputs for each grid cell at 6-hourly intervals from weekly outputs <br>
     
     * [vic/runoff-subset-by-huc2.py](.vic/runoff-subset-by-huc2.py): <br>
     extract [GRFR ReachHydro](https://www.reachhydro.org/home/records/grfr) runoff for each grid cell for calibration <br>
     
     * [vic/calibration/run_vic_impi.py](./vic/calibration/run_vic_impi.py): <br>
     set up a cycle of calibration routines for each grid cell <br>
     
     * [vic/calibration/run-calibration-impi.py](./vic/calibration/run-calibration-impi.py): <br>
     run the calibration routines with OSTRICH for all grid cells and simulate runoff based on calibrated VIC parameters <br>
     
  3. `mosartwmpy/`: runoff routing through river networks with water managements, including reservoir operations <br>
     * [mosartwmpy/create_MOSART_CA_domain.py](./mosartwmpy/create_MOSART_CA_domain.py): <br>
     create mosartwmpy domain parameters for Western Canada at 1/8th degree resolution <br>
     
     * [mosartwmpy/mask_MOSART_CA_domain.py](./mosartwmpy/mask_MOSART_CA_domain.py): <br>
     mask the domain parameters for areas of interest, excluding water bodies <br>
     
     * [mosartwmpy/create_MOSART_CA_runoff.py](./mosartwmpy/create_MOSART_CA_runoff.py): <br>
     create mosartwmpy runoff inputs by aggregating VIC runoff outputs into mosartwmpy grids at 1/8th degree resolution <br>
     
     * [mosartwmpy/create_MOSART_CA_mask.py](./mosartwmpy/create_MOSART_CA_mask.py): <br>
     mask the mosartwmpy runoff if necessary, e.g., TGW boundary effects <br>
     
     * [mosartwmpy/MOSART_CA.py](./mosartwmpy/MOSART_CA.py): <br>
     run mosartwmpy <br>
     
     * [mosartwmpy/create_reservoir_flow_monthly_mean.py](./mosartwmpy/create_reservoir_flow_monthly_mean.py): <br>
     extract monthly-mean flow at reservoirs for generic operation rules from the mosartwmpy run with water management disabled <br>
     
  5. `hydropower-scaling/`: streamflow scaling to produce hydropower estimates <br>
     * [hydropower-scaling/extract_gindex_flow.py](./hydropower-scaling/extract_gindex_flow.py): <br>
     extract regulated streamflow ouputs from the mosartwmpy run with water management enabled <br>
     
     * [hydropower-scaling/calculate_scalingfactor.py](./hydropower-scaling/calculate_scalingfactor.py): <br>
     derive scaling factors for hydropower generation relative to streamflow for reference year, one with no constraint and the other with intake flow rate constraints <br>
     
     * [hydropower-scaling/produce_hydropower_data.py](./hydropower-scaling/produce_hydropower_data.py): <br>
     produce hydropower estimates for other years using the derived hydropower scaling factors <br>

---
## Code Execution Steps
### VIC Runoff Modeling
   1. Compile [VIC](https://vic.readthedocs.io/en/master/) and [OSTRICH](https://www.eng.buffalo.edu/~lsmatott/Ostrich/OstrichMain.html), by following the instructions at the respective links.
   2. Download [VICGlobal](https://zenodo.org/record/5038653/) domain parameters and unpack the files, `namerica_domain.nc` and `nameria_params.nc`.
   3. Run `vic/grid_ids_ca.py` to create a list of VIC grids `vic/output/grid_ids_ca_check.csv` for Western Canada, based on watershed delineations `vic/input/NHN_Subset_Rev2.shp` and `vic/input/T2_bounds.shp`.
   4. Run `vic/param-subset-by-huc2.sl` on a HPC system to extract **VICGlobal** domain parameters on VIC grids.
   5. Download [TGW](https://tgw-data.msdlive.org/) meteorological forcing data. (Warning: the data is very large and will require a HPC system to process)
   6. Run `vic/proc_wrf_to_vicgrid_00625_parallel.sl` to convert **TGW** historical climate run into weekely meteorological forcing data on VIC grids at 1/16th degree resolution.
   7. Run `vic/conus-forcings-by-huc2-from-weekly.sl` to generate VIC meteorological forcing for each grid cell at 6-hourly intervals from weekly outputs.
   8. Download [GRFR ReachHydro](https://www.reachhydro.org/home/records/grfr) runoff data for VIC model calibration.
   9. Run `vic/runoff-subset-by-huc2.sl` to extract **GRFR ReachHydro** runoff for each grid cell for calibration.
   10. Run `vic/calibration/run-calibration-ca.sl` to run the calibration routines with OSTRICH for all grid cells and simulate runoff based on calibrated VIC parameters.

### mosartwmpy Streamflow Routing with Water Management
   1. Install [mosartwmpy](https://mosartwmpy.readthedocs.io/en/latest/), by following the instructions at the link.
   2. Run `mosartwmpy/create_MOSART_CA_domain.py` to create mosartwmpy domain parameters `mosartwmpy/output/MOSART_CA_8th_20240104.nc` for Western Canada at 1/8th degree resolution.
   3. Run `mosartwmpy/mask_MOSART_CA_domain.py` to mask the domain parameters (`mosartwmpy/output/MOSART_CA_8th_20240104_masked.nc`) for areas of interest, excluding water bodies based on `mosartwmpy/input/grids_ca_attr_basinmasked.csv`. <br>
   4. Run `mosartwmpy/create_MOSART_CA_runoff.sl` on a HPC system to create mosartwmpy runoff inputs by aggregating VIC runoff outputs into mosartwmpy grids at 1/8th degree resolution.
   5. Run `mosartwmpy/create_MOSART_CA_mask.py` to mask the mosartwmpy runoff if necessary, e.g., TGW boundary effects (`mosartwmpy/input/runoff_mask_on_mosartwmpy.nc`). <br>
   6. Run `mosartwmpy/MOSART_CA.sl` after initializing with `mosartwmpy/input/config_noWM.yaml` on `mosartwmpy/MOSART_CA.py` to run mosartwmpy with water management disabled.
   7. Run `mosartwmpy/create_reservoir_flow_monthly_mean.py` to extract monthly-mean flow at reservoirs for generic operation rules from the mosartwmpy run with water management disabled.
   8. Run `mosartwmpy/MOSART_CA.sl` again, but initializing with `mosartwmpy/input/config_WM.yaml` on `mosartwmpy/MOSART_CA.py` to run mosartwmpy with water management enabled.

### Hydropower Scaling
   1. Download `CAN_hydropower_facilities&scaling.csv` from the [Zenodo](https://zenodo.org/record/14984725) repository.
   2. Run `hydropower-scaling/extract_gindex_flow.py` to extract regulated streamflow ouputs from the final mosartwmpy run
   3. Run `hydropower-scaling/calculate_scalingfactor.py` to derive scaling factors for hydropower generation relative to streamflow for reference year, one with no constraint and the other with intake flow rate constraints
   4. Run `hydropower-scaling/produce_hydropower_data.py` to produce hydropower estimates for other years, including **Monthly Hydropower Generation Estimates** and **Flexibility Metrics**

---

## Documentation
For more details about the hydrology-hydropower modeling approach, please refer to the following publication:
  - Son, Y., Bracken, C., Daniel, B., and Voisin, N. (2025). Monthly hydropower generation data for Western Canada to support Western-US interconnect power system studies [in revision].

---

## Funding Acknowledgements
This work was supported by the Grid Operations, Decarbonization, Environmental and Energy Equity Platform (GODEEEP) Investment, under the Laboratory Directed Research and Development (LDRD) Program at the Pacific Northwest National Laboratory (PNNL). <br>
The PNNL is a multi-program national laboratory operated by Battelle Memorial Institute for the U.S. Department of Energy (DOE) under Contract No. DE-AC05-76RL01830.
