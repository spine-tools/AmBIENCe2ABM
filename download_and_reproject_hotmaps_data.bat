TITLE Clone and reproject Hotmaps data.
CALL git clone https://gitlab.com/hotmaps/gfa_res_curr_density.git "data_sources/gfa_res_curr_density/"
CALL git clone https://gitlab.com/hotmaps/gfa_nonres_curr_density.git "data_sources/gfa_nonres_curr_density/"
CALL rio warp "data_sources/gfa_res_curr_density/data/gfa_res_curr_density.tif" "data_sources/gfa_res_curr_density/data/gfa_res_curr_density_epsg4326.tif" --dst-crs EPSG:4326
CALL rio warp "data_sources/gfa_nonres_curr_density/data/gfa_nonres_curr_density.tif" "data_sources/gfa_nonres_curr_density/data/gfa_nonres_curr_density_epsg4326.tif" --dst-crs EPSG:4326