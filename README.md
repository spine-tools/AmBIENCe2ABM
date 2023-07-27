# AmBIENCe2ABM

A Python package for processing [AmBIENCe project](https://ambience-project.eu/) EU-wide building stock datasets for
[ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel).


## Key contents

1. `abm_data/` contains the raw `.csv` files of the processed output data contained within the output [Data Package](https://specs.frictionlessdata.io//data-package/).
2. `ambience_data/` contains the raw input data files for the processing.
3. `assumptions/` contains auxiliary data that needs to be assumed in order to complete the final dataset for ABM.jl.
4. `src/` contains the Julia source code for the `AmBIENCE2ABM` module.
5. `datapackage.json` is the [Data Package](https://specs.frictionlessdata.io//data-package/) definition of the processed output.


## Installation

TODO.


## Usage

TODO.


## Documentation

TODO.


## License

The AmBIENCe2ABM code is licensed under the [MIT License](https://mit-license.org/).
See `LICENSE` for more information.

The processed data and the resulting included datapackage are licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).


## How to cite

For the moment, this GitHub page is the only way to reference this piece of code, e.g.:

```
Topi Rasku. 2023. AmBIENCe2ABM.jl: A Julia module for processing AmBIENCe project EU-wide building stock datasets for ArchetypeBuildingModel.jl.. Software. GitHub, https://github.com/spine-tools/AmBIENCe2ABM.
```


## References

This module is built on top of the [AmBIENCe project public deliverables](https://ambience-project.eu/deliverables/#public-deliverables):
1. "[D4.1 Database of grey-box model parameter values for EU building typologies](https://ambience-project.eu/wp-content/uploads/2022/02/AmBIENCe_D4.1_Database-of-grey-box-model-parameter-values-for-EU-building-typologies-update-version-2-submitted.pdf)",
2. "[Database of grey-box model parameters](https://ambience-project.eu/wp-content/uploads/2022/03/AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx)",
3. "[D4.2 - Buildings Energy Systems Database EU27](https://ambience-project.eu/wp-content/uploads/2022/06/AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx)".

Shapefiles for the relevant EU-countries were obtained from [Natural Earth](https://www.naturalearthdata.com/):
4. "[1:10m Cultural Vectors, Admin 0 - Countries without boundary lakes: ne_10m_admin_0_countries_lakes.zip](https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries_lakes.zip)"

Estimated heated gross floor area density raster data obtained from the [Hotmaps project](https://www.hotmaps-project.eu/) outputs:
> Simon Pezzutto, Stefano Zambotti, Silvia Croce, Pietro Zambelli, Giulia Garegnani, Chiara Scaramuzzino, Ramón Pascual Pascuas, Alyona Zubaryeva, Franziska Haas, Dagmar Exner (EURAC), Andreas Mueller (e-think), Michael Hartner (TUW), Tobias Fleiter, Anna-Lena Klingler, Matthias Ku¨hnbach, Pia Manz, Simon Marwitz, Matthias Rehfeldt, Jan Steinbach, Eftim Popovski (Fraunhofer ISI) Reviewed by Lukas Kranzl, Sara Fritz (TUW). Hotmaps Project, D2.3 WP2 Report – Open Data Set for the EU28, 2018 www.hotmaps-project.eu.
5.  "[Heated gross floor area density map of residential buildings in EU28 + Switzerland, Norway and Iceland for the year 2015](https://gitlab.com/hotmaps/gfa_res_curr_density)"
6. Simon Pezzutto, Stefano Zambotti, Silvia Croce, Pietro Zambelli, Giulia Garegnani, Chiara Scaramuzzino, Ramón Pascual Pascuas, Alyona Zubaryeva, Franziska Haas, Dagmar Exner (EURAC), Andreas Mueller (e-think), Michael Hartner (TUW), Tobias Fleiter, Anna-Lena Klingler, Matthias Ku¨hnbach, Pia Manz, Simon Marwitz, Matthias Rehfeldt, Jan Steinbach, Eftim Popovski (Fraunhofer ISI) Reviewed by Lukas Kranzl, Sara Fritz (TUW). Hotmaps Project, D2.3 WP2 Report – Open Data Set for the EU28, 2018 www.hotmaps-project.eu. "[Heated gross floor area density map of non-residential buildings in EU28 + Switzerland, Norway and Iceland for the year 2015](https://gitlab.com/hotmaps/gfa_nonres_curr_density)"


## Acknowledgements

<center>
<table width=500px frame="none">
<tr>
<td valign="middle" width=100px>
<img src=https://european-union.europa.eu/themes/contrib/oe_theme/dist/eu/images/logo/standard-version/positive/logo-eu--en.svg alt="EU emblem" width=100%></td>
<td valign="middle">This work was supported by EU project Mopo (2023-2026), which has received funding from European Climate, Infrastructure and Environment Executive Agency under the European Union’s HORIZON Research and Innovation Actions under grant agreement N°101095998.</td>
</table>
</center>