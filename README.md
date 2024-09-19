# tgw-hydro-canada
A collection of scripts to produce monthly hydropower generation estimates for 110 facilities in British Columbia and Alberta to support the Western-US Interconnect grid system studies. The dataset is published in the Zenodo repository and can be accessed at the following link: https://zenodo.org/record/13760827 (DOI: 10.5281/zenodo.13760826)."

## Code Descriptions
  1. vic: hydrologic modeling to generate runoff <br>
     **/vic** <br>
     /vic/grid_ids_ca.py: <br>
     /vic/param-subset-by-huc2.py: <br>
     /vic/proc_wrf_to_vicgrid_00625_parallel.py: <br>
     /vic/conus-forcings-by-huc2-from-weekly.py: <br>
     /vic/runoff-subset-by-huc2.py: <br>
     **/vic/calibration** <br>
     /vic/calibration/run_vic_impi.py: <br>
     /vic/calibration/run-calibration-impi.py: <br>
  3. mosartwmpy: runoff routing through river networks with water managements (reservoir operations) <br>
     **/mosartwmpy** <br>
     /mosartwmpy/create_MOSART_CA_domain.py: <br>
     /mosartwmpy/mask_MOSART_CA_domain.py: <br>
     /mosartwmpy/create_MOSART_CA_runoff.py: <br>
     /mosartwmpy/create_MOSART_CA_mask.py: <br>
     /mosartwmpy/create_reservoir_flow_monthly_mean.py: <br>
     /mosartwmpy/MOSART_CA.py: <br>
  5. hydropower-scaling: streamflow scaling to produce hydropower estimates <br>
     **/hydropower-scaling** <br>
     /hydropower-scaling/extract_gindex_flow.py: <br>
     /hydropower-scaling/calculate_scalingfactor.py: <br>
     /hydropower-scaling/produce_hydropower_data.py: <br>

## Documentation
For more details about the hydrology-hydropower modeling approach, please refer to the following publication:
  - Son, Y., Bracken, C., Daniel, B., and Voisin, N. (2024). A monthly hydropower generation dataset for Western Canada to support Western-US interconnect grid system studies [Manuscript submitted for publication].


## Funding Acknowledgements
This work was supported by the Grid Operations, Decarbonization, Environmental and Energy Equity Platform (GODEEEP) Investment, under the Laboratory Directed Research and Development (LDRD) Program at the Pacific Northwest National Laboratory (PNNL). <br>
The PNNL is a multi-program national laboratory operated by Battelle Memorial Institute for the U.S. Department of Energy (DOE) under Contract No. DE-AC05-76RL01830.
