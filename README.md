# AmBIENCe2ABM

A Python package for processing [AmBIENCe project](https://ambience-project.eu/) EU-wide building stock datasets for
[ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel).

>[!NOTE]
>The AmBIENCe project deliverables used as raw data for this tool are not included under `data_sources/ambience/` because their licensing is yet unclear.
>Please refer to the References section for where to find the required raw data deliverables.

>[!WARNING]
>The heat source distributions according to the AmBIENCe data seem highly unreliable, use at own risk!
>Aggregating over the heat source distributions recommended.

>[!WARNING]
>The geometries of some of the reference buildings seem highly unrealistic, especially for Cyprus.
>High level of aggregation over the building stock recommended.

>[!CAUTION]
>The AmBIENCe dataset contains no parameters for ventilation and infiltration, which can account for 50+% of building heat losses.
>Currently, crude assumptions based on the [EPISCOPE-TABULA](https://episcope.eu/welcome/) results are used instead.


## Key contents

1. `data/` contains the raw `.csv` files of the processed output building stock [Data Package](https://specs.frictionlessdata.io//data-package/).
2. `data_assumptions/` contains auxiliary data that needs to be assumed in order to complete the final dataset for ABM.jl.
3. `data_sources/` contains the raw input data files for the processing.
4. `definitions` contains the raw `.csv` files for the processed reference building definition [Data Package](https://specs.frictionlessdata.io//data-package/).
5. `definitions_assumptions` contains auxiliary definitions required to complete the definitions for ABM.jl.
6. `src/` contains the source code for the `AmBIENCE2ABM` module.
7. `data.json` is the [Data Package](https://specs.frictionlessdata.io//data-package/) definition of the processed building stock data output.
8. `definitions.json` is the [Data Package](https://specs.frictionlessdata.io//data-package/) definition of the processed reference building definitions.
9. `download_and_reproject_hotmaps_data.bat` a script for downloading and reprojecting the required Hotmaps data.
10. `import_ambience2abm_data.json` is the [Spine Toolbox](https://github.com/Spine-tools/Spine-Toolbox) importer specification for `data.json`.
11. `import_ambience2abm_definitions.json` is the [Spine Toolbox](https://github.com/Spine-tools/Spine-Toolbox) importer specification for `definitions.json`.
12. `update_datapackage.py` is the main program file for updating the [Data Package](https://specs.frictionlessdata.io//data-package/)s.


## Installation

In order to follow the installation steps below, you need to have the following
software installed on your computer and in your `PATH`:
1. [Git](https://www.git-scm.com/)
2. [Python](https://www.python.org/) *(along with `pip`)*

Since this package is not indexed in online package repositories,
you need to download or clone this repository on your machine.
E.g. using Git: 
```
git clone https://github.com/spine-tools/AmBIENCe2ABM.git
```
Once you have the repository on your computer,
navigate into this root folder *(the one containing this `README.md`)*.
Then, open the command line and install this package and its dependencies via
```
pip install -e .
```

### Manually downloading the required AmBIENCe project data.

Due to yet unclear licensing of the AmBIENCe project deliverables,
the required input data files aren't included in this repository.
However, they can be downloaded under `data_sources/ambience/`
from the links provided in the References section below.

**NOTE! These aren't necessary if you're only interested in using the provided Data Packages, but are necessary if you want to update the datapackage after some changes.**


### Downloading and reprojecting the required Hotmaps data.

This package relies on heated gross floor area density GIS raster data
produced in the [Hotmaps project](https://www.hotmaps-project.eu/)
*(see the References section below)*.
The `download_and_reproject_hotmaps_data.bat` script should automatically
clone and reproject the required data, as long as [Git](https://www.git-scm.com/)
and the [rasterio](https://pypi.org/project/rasterio/)
*(a python dependency of this module)* are found in your `PATH`.

**NOTE! The EU-wide floor area density raster datasets are around ~200MB each, and the reprojections essentially duplicate the data, resulting in ~800MB of stuff. Downloading and reprojecting the data can take several minutes.**

#### Manually downloading the required Hotmaps data.

You can either download the necessary repositories manually
under the `data_sources/` folder, or clone them using Git via:
```
git clone https://gitlab.com/hotmaps/gfa_res_curr_density.git "data_sources/gfa_res_curr_density/"
git clone https://gitlab.com/hotmaps/gfa_nonres_curr_density.git "data_sources/gfa_nonres_curr_density/"
```

#### Manually reprojecting Hotmaps data.

The Hotmaps heated floor area raster data uses EPSG:3035 for its coordinate
reference system, while PyPSA/atlite and ERA5 mainly work using EPSG:4326.
Thus, one needs to reproject the raster data to the desired CRS.
This can be done e.g. using [rasterio](https://github.com/rasterio/rasterio) `rio warp`.

Rasterio can be installed simply via
```
pip install rasterio
```
after which, the `rio warp` command line program can be used to reproject the raster data:
```
rio warp gfa_res_curr_density.tif gfa_res_curr_density_epsg4326.tif --dst-crs EPSG:4326
```
**NOTE! The raster datasets are quite large, and the reprojection can take several minutes.**


## Use

This module produces and contains the processed EU-level building stock data as
a [Data Package](https://specs.frictionlessdata.io//data-package/).
For most use cases, I imagine the contents of the `data/` folder and the `data.json` are sufficient.

The `import_ambience2abm_data.json` contains the
[Spine Toolbox](https://github.com/Spine-tools/Spine-Toolbox)
importer specification which can be used to import the data into a Spine Datastore.
Since [ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel)
is built on top of Spine Datastores, this is more or less the intended use for this module.
Please refer to the [Spine Toolbox](https://github.com/Spine-tools/Spine-Toolbox)
documentation for how to set up importer specifications.

For mode advanced use of the package,
the `data_testscript.ipynb` can perhaps provide some examples.


### Updating the data package

Updating the data package has been automatised via the `update_datapackage.py` python program,
in case the underlying `data_sources/`, `data_assumptions/`, or the keyword arguments are changed.
The `update_datapackage.py` takes two optional keyword arguments:

1. `--ind 0.1`: Abbreviated from *interior node depth*. Corresponds to The assumed depth of the structural temperature nodes, given as a fraction of the total thermal resistance of the structure from its interior surface up to the middle of its insulation, or its own middle point if no insulation like is assumed for internal structures *(partition walls and separating floors)*.
2. `--pov 1209600`: Abbreviated from *period of variations*. The assumed period of variations in seconds for the *'EN ISO 13786:2017 Annex C.2.4 Effective thickness method'* for estimating the effective thermal mass of the structures.
3. `--extrapolate True`: A boolean flag to extrapolate data for new countries. See `update_datapackage.py` for the extrapolation settings.

The default values for the above parameters are based on calibrations
performed in [this publication](https://doi.org/10.3390/buildings14061614).


## Documentation

Currently this `README.md` is all you've got besides the docstrings in the code.


## License

The AmBIENCe2ABM code is licensed under the [MIT License](https://mit-license.org/).
See `LICENSE` for more information.

The processed data and the resulting included datapackage are licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).

The different data sources have different licenses,
please refer to them individually.


## How to cite

For the moment, this GitHub page is the only way to reference this repository, e.g.:

```
Topi Rasku. 2023. AmBIENCe2ABM: A Python package for processing AmBIENCe project EU-wide building stock datasets for ArchetypeBuildingModel.jl. Software. GitHub, https://github.com/spine-tools/AmBIENCe2ABM.
```


## References

This module is built on top of the [AmBIENCe project public deliverables](https://ambience-project.eu/deliverables/#public-deliverables) *(license currently unclear, but publicly available through the project website.)*:

1. "[D4.1 Database of grey-box model parameter values for EU building typologies](https://ambience-project.eu/wp-content/uploads/2022/02/AmBIENCe_D4.1_Database-of-grey-box-model-parameter-values-for-EU-building-typologies-update-version-2-submitted.pdf)".
2. "[Database of grey-box model parameters](https://ambience-project.eu/wp-content/uploads/2022/03/AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx)".
3. "[D4.2 - Buildings Energy Systems Database EU27](https://ambience-project.eu/wp-content/uploads/2022/06/AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx)".

Shapefiles for the relevant EU-countries were obtained from [Natural Earth](https://www.naturalearthdata.com/) *(public domain)*:

4. "[1:10m Cultural Vectors, Admin 0 - Countries without boundary lakes: ne_10m_admin_0_countries_lakes.zip](https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries_lakes.zip)"

Estimated heated gross floor area density raster data obtained from the [Hotmaps project](https://www.hotmaps-project.eu/) outputs *(CC-BY-4.0)*:
> Simon Pezzutto, Stefano Zambotti, Silvia Croce, Pietro Zambelli, Giulia Garegnani, Chiara Scaramuzzino, Ramón Pascual Pascuas, Alyona Zubaryeva, Franziska Haas, Dagmar Exner (EURAC), Andreas Mueller (e-think), Michael Hartner (TUW), Tobias Fleiter, Anna-Lena Klingler, Matthias Ku¨hnbach, Pia Manz, Simon Marwitz, Matthias Rehfeldt, Jan Steinbach, Eftim Popovski (Fraunhofer ISI) Reviewed by Lukas Kranzl, Sara Fritz (TUW). Hotmaps Project, D2.3 WP2 Report – Open Data Set for the EU28, 2018 www.hotmaps-project.eu.

5. "[Heated gross floor area density map of residential buildings in EU28 + Switzerland, Norway and Iceland for the year 2015](https://gitlab.com/hotmaps/gfa_res_curr_density)"
6. "[Heated gross floor area density map of non-residential buildings in EU28 + Switzerland, Norway and Iceland for the year 2015](https://gitlab.com/hotmaps/gfa_nonres_curr_density)"

Assumed ventilation properties are based on the [results of the TABULA project](https://episcope.eu/communication/download/):

7. "[tabula-values.xlsx](https://episcope.eu/fileadmin/tabula/public/calc/tabula-values.xlsx)", `Tab.BoundaryCond` sheet `n_air_use` column for ventilation rate, `Tab.Const.Infiltration` for infiltration rate. Ventilation heat recovery assumed non-existent.


## Acknowledgements

<center>
<table width=500px frame="none">
<tr>
<td valign="middle" width=100px>
<img src=https://european-union.europa.eu/themes/contrib/oe_theme/dist/eu/images/logo/standard-version/positive/logo-eu--en.svg alt="EU emblem" width=100%></td>
<td valign="middle">This work was supported by EU project Mopo (2023-2026), which has received funding from European Climate, Infrastructure and Environment Executive Agency under the European Union’s HORIZON Research and Innovation Actions under grant agreement N°101095998.</td>
</table>
</center>