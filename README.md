# tgw-hydro-canada
A collection of scripts to produce monthly hydropower generation estimates for 110 facilities in British Columbia and Alberta to support the Western-US Interconnect grid system studies. The dataset is published in the Zenodo repository and can be accessed at the following link: https://zenodo.org/record/13760827 (DOI: 10.5281/zenodo.13760826)."

## Code Descriptions
  1. ***vic/***: hydrologic modeling to generate runoff <br>
  
     -&nbsp;*vic/grid_ids_ca.py*: <br>
     >create a list of VIC grids for Western Canada <br>
     
     -&nbsp;*vic/param-subset-by-huc2.py*: <br>
     >create VIC domain parameters from VICGlobal <br>
     
     -&nbsp;*vic/proc_wrf_to_vicgrid_00625_parallel.py*: <br>
     
     >convert TGW historical climate run into weekely meteorological forcing data at 1/16th degree <br>
     
     -&nbsp;*vic/conus-forcings-by-huc2-from-weekly.py*: <br>
     >create VIC meteorological forcing inputs at 6-hourly intervals from weekly outputs <br>
     
     -&nbsp;*vic/runoff-subset-by-huc2.py*: <br>
     >extract GRFR ReachHydro runoff for VIC grids for calibration <br>
     
     -&nbsp;*vic/calibration/run_vic_impi.py*: <br>
     >set up a cycle of calibration routines for each grid cell <br>
     
     -&nbsp;*vic/calibration/run-calibration-impi.py*: <br>
     >run the calibration routines with OSTRICH for all grid cells within HUC <br>
     
  3. ***mosartwmpy/***: runoff routing through river networks with water managements, including reservoir operations <br>
  
     -&nbsp;*mosartwmpy/create_MOSART_CA_domain.py*: <br>
     >create mosartwmpy domain parameters for Western Canada <br>
     
     -&nbsp;*mosartwmpy/mask_MOSART_CA_domain.py*: <br>
     >mask the domain parameters for areas of interest, excluding water bodies <br>
     
     -&nbsp;*mosartwmpy/create_MOSART_CA_runoff.py*: <br>
     >create mosartwmpy runoff inputs by aggregating VIC runoff outputs into mosartwmpy grids at 1/8th degree resolution <br>
     
     -&nbsp;*mosartwmpy/create_MOSART_CA_mask.py*: <br>
     >mask the mosartwmpy runoff if necessary, e.g., TGW boundary effects <br>
     
     -&nbsp;*mosartwmpy/MOSART_CA.py*: <br>
     >run mosartwmpy <br>
     
     -&nbsp;*mosartwmpy/create_reservoir_flow_monthly_mean.py*: <br>
     >extract monthly-mean flow at reservoirs for generic operation rules from the mosartwmpy run with water management disabled <br>
     
  5. ***hydropower-scaling/***: streamflow scaling to produce hydropower estimates <br>
  
     -&nbsp;*hydropower-scaling/extract_gindex_flow.py*: <br>
     >extract regulated streamflow ouputs from the mosartwmpy run with water management enabled <br>
     
     -&nbsp;*hydropower-scaling/calculate_scalingfactor.py*: <br>
     >derive scaling factors for hydropower generation relative to streamflow for reference year, one with no cap and the other with a diversion inflow cap <br>
     
     -&nbsp;*hydropower-scaling/produce_hydropower_data.py*: <br>
     >produce hydropower estimates for other years using the derived hydropower scaling factors <br>

## Documentation
For more details about the hydrology-hydropower modeling approach, please refer to the following publication:
  - Son, Y., Bracken, C., Daniel, B., and Voisin, N. (2024). A monthly hydropower generation dataset for Western Canada to support Western-US interconnect grid system studies [Manuscript submitted for publication].


## Funding Acknowledgements
This work was supported by the Grid Operations, Decarbonization, Environmental and Energy Equity Platform (GODEEEP) Investment, under the Laboratory Directed Research and Development (LDRD) Program at the Pacific Northwest National Laboratory (PNNL). <br>
The PNNL is a multi-program national laboratory operated by Battelle Memorial Institute for the U.S. Department of Energy (DOE) under Contract No. DE-AC05-76RL01830.
