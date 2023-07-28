# AmBIENCe2ABM

A Python package for processing [AmBIENCe project](https://ambience-project.eu/) EU-wide building stock datasets for
[ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel).

**This package is still a work in progress! First complete version expected sometime in late Summer 2023.**


## Key contents

1. `ambience_data/` contains the raw AmBIENCe input data files for the processing.
2. `assumptions/` contains auxiliary data that needs to be assumed in order to 
3. `data/` contains the raw `.csv` files of the processed output data contained within the output [Data Package](https://specs.frictionlessdata.io//data-package/).
complete the final dataset for ABM.jl.
4. `natural_earth/` contains the relevant EU-countries shapefile.
5. `src/` contains the Julia source code for the `AmBIENCE2ABM` module.
6. `datapackage.json` is the [Data Package](https://specs.frictionlessdata.io//data-package/) definition of the processed output.
7. `import_ambience2abm.json` is the [Spine Toolbox](https://github.com/Spine-tools/Spine-Toolbox) importer specification for the `datapackage.json`.
8. `update_datapackage.py` is the main program file for updating


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

### Downloading the required Hotmaps data.

This package relies on heated gross floor area density GIS raster data
produced in the [Hotmaps project](https://www.hotmaps-project.eu/) *(see the References section below)*.
You can either download the necessary repositories into this root folder,
or clone them using Git via:
```
git clone https://gitlab.com/hotmaps/gfa_res_curr_density.git
git clone https://gitlab.com/hotmaps/gfa_nonres_curr_density.git
```


## Usage

This module produces and contains the processed EU-level building stock data as
a [Data Package](https://specs.frictionlessdata.io//data-package/).
For most use cases, I imagine the contents of the `data/` folder and the `datapackage.json` are sufficient.

The `import_ambience2abm.json` contains the
[Spine Toolbox](https://github.com/Spine-tools/Spine-Toolbox)
importer specification which can be used to import the data into a Spine Datastore.
Since [ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel)
is built on top of Spine Datastores, this is more or less the intended use for this module.
Please refer to the [Spine Toolbox](https://github.com/Spine-tools/Spine-Toolbox)
documentation for how to set up importer specifications.

For mode advanced use of the package,
the `testscript.ipynb` can perhaps provide some examples.


### Updating the data package

Updating the data package has been automatised via the `update_datapackage.py` python program,
in case the underlying `ambience_data/`, `assumptions/`, or the keyword arguments are changed.
The `update_datapackage.py` takes two optional keyword arguments:

1. `--ind 0.1`: Abbreviated from *interior node depth*. Corresponds to The assumed depth of the structural temperature nodes, given as a fraction of the total thermal resistance of the structure from its interior surface up to the middle of its insulation, or its own middle point if no insulation like is assumed for internal structures *(partition walls and separating floors)*.
2. `--pov 2225140`: Abbreviated from *period of variations*. The assumed period of variations in seconds for the *'EN ISO 13786:2017 Annex C.2.4 Effective thickness method'* for estimating the effective thermal mass of the structures.

Note that the default values for the above parameters are currently based on
calibrations performed in a [preprint](https://doi.org/10.5281/zenodo.7623739),
and are subject to change.


## Documentation

Currently this `README.md` is all you've got besides the docstrings in the code.


## License

The AmBIENCe2ABM code is licensed under the [MIT License](https://mit-license.org/).
See `LICENSE` for more information.

The processed data and the resulting included datapackage are licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).


## How to cite

For the moment, this GitHub page is the only way to reference this repository, e.g.:

```
Topi Rasku. 2023. AmBIENCe2ABM: A Python package for processing AmBIENCe project EU-wide building stock datasets for ArchetypeBuildingModel.jl.. Software. GitHub, https://github.com/spine-tools/AmBIENCe2ABM.
```


## References

This module is built on top of the [AmBIENCe project public deliverables](https://ambience-project.eu/deliverables/#public-deliverables) *(license currently unclear, but publicly available through the project website.)*:

1. "[D4.1 Database of grey-box model parameter values for EU building typologies](https://ambience-project.eu/wp-content/uploads/2022/02/AmBIENCe_D4.1_Database-of-grey-box-model-parameter-values-for-EU-building-typologies-update-version-2-submitted.pdf)",
2. "[Database of grey-box model parameters](https://ambience-project.eu/wp-content/uploads/2022/03/AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx)",
3. "[D4.2 - Buildings Energy Systems Database EU27](https://ambience-project.eu/wp-content/uploads/2022/06/AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx)".

Shapefiles for the relevant EU-countries were obtained from [Natural Earth](https://www.naturalearthdata.com/) *(public domain)*:

4. "[1:10m Cultural Vectors, Admin 0 - Countries without boundary lakes: ne_10m_admin_0_countries_lakes.zip](https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries_lakes.zip)"

Estimated heated gross floor area density raster data obtained from the [Hotmaps project](https://www.hotmaps-project.eu/) outputs *(CC-BY-4.0)*:
> Simon Pezzutto, Stefano Zambotti, Silvia Croce, Pietro Zambelli, Giulia Garegnani, Chiara Scaramuzzino, Ramón Pascual Pascuas, Alyona Zubaryeva, Franziska Haas, Dagmar Exner (EURAC), Andreas Mueller (e-think), Michael Hartner (TUW), Tobias Fleiter, Anna-Lena Klingler, Matthias Ku¨hnbach, Pia Manz, Simon Marwitz, Matthias Rehfeldt, Jan Steinbach, Eftim Popovski (Fraunhofer ISI) Reviewed by Lukas Kranzl, Sara Fritz (TUW). Hotmaps Project, D2.3 WP2 Report – Open Data Set for the EU28, 2018 www.hotmaps-project.eu.

5. "[Heated gross floor area density map of residential buildings in EU28 + Switzerland, Norway and Iceland for the year 2015](https://gitlab.com/hotmaps/gfa_res_curr_density)"
6. "[Heated gross floor area density map of non-residential buildings in EU28 + Switzerland, Norway and Iceland for the year 2015](https://gitlab.com/hotmaps/gfa_nonres_curr_density)"


## Acknowledgements

<center>
<table width=500px frame="none">
<tr>
<td valign="middle" width=100px>
<img src=https://european-union.europa.eu/themes/contrib/oe_theme/dist/eu/images/logo/standard-version/positive/logo-eu--en.svg alt="EU emblem" width=100%></td>
<td valign="middle">This work was supported by EU project Mopo (2023-2026), which has received funding from European Climate, Infrastructure and Environment Executive Agency under the European Union’s HORIZON Research and Innovation Actions under grant agreement N°101095998.</td>
</table>
</center>