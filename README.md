# AmBIENCe2ABM.jl

A Julia module for processing [AmBIENCe project](https://ambience-project.eu/) EU-wide building stock datasets for
[ArchetypeBuildingModel.jl.](https://github.com/vttresearch/ArchetypeBuildingModel).


## Key contents

1. `abm_data/` contains the raw `.csv` files of the processed output data contained within the output [Data Package](https://specs.frictionlessdata.io//data-package/).
2. `ambience_data/` contains the raw input data files for the processing.
3. `assumptions/` contains auxiliary data that needs to be assumed in order to complete the final dataset for ABM.jl.
4. `src/` contains the Julia source code for the `AmBIENCE2ABM.jl` module.
5. `datapackage.json` is the [Data Package](https://specs.frictionlessdata.io//data-package/) definition of the processed output.


## Installation

TODO.


## Usage

TODO.


## Documentation

TODO.


## License

The AmBIENCe2ABM.jl code is licensed under the [MIT License](https://mit-license.org/).
See `LICENSE` for more information.

The processed data and the resulting included datapackage are licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).


## How to cite

For the moment, this GitHub page is the only way to reference this piece of code, e.g.:

```
Topi Rasku. 2023. AmBIENCe2ABM.jl: A Julia module for processing AmBIENCe project EU-wide building stock datasets for ArchetypeBuildingModel.jl.. Software. GitHub, https://github.com/spine-tools/AmBIENCe2ABM.jl.
```


## References

This module is built on top of the [AmBIENCe project public deliverables](https://ambience-project.eu/deliverables/#public-deliverables),
namely, the "[D4.1 Database of grey-box model parameter values for EU building typologies](https://ambience-project.eu/wp-content/uploads/2022/02/AmBIENCe_D4.1_Database-of-grey-box-model-parameter-values-for-EU-building-typologies-update-version-2-submitted.pdf)",
the accompanying "[Database of grey-box model parameters](https://ambience-project.eu/wp-content/uploads/2022/03/AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx)",
as well as the "[D4.2 - Buildings Energy Systems Database EU27](https://ambience-project.eu/wp-content/uploads/2022/06/AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx)".


## Acknowledgements

<center>
<table width=500px frame="none">
<tr>
<td valign="middle" width=100px>
<img src=https://european-union.europa.eu/themes/contrib/oe_theme/dist/eu/images/logo/standard-version/positive/logo-eu--en.svg alt="EU emblem" width=100%></td>
<td valign="middle">This work was supported by EU project Mopo (2023-2026), which has received funding from European Climate, Infrastructure and Environment Executive Agency under the European Union’s HORIZON Research and Innovation Actions under grant agreement N°101095998.</td>
</table>
</center>