# AmBIENCe2ABM/data_assumptions

Contains data assumptions required for processing the building stock dataset.

This data package is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
as indicated by the master `README.md`.
See brief explanations of the contents below:


## building_stock.csv

TBD


## building_type_mappings.csv

Maps `building_type` to either `residential` or `non-residential`.

This is done to correctly assign the Hotmaps raster weights,
see `data_sources/gfa_res_curr_density` and
`data_sources/gfa_nonres_curr_density`.


## fenestration.csv

Contains assumed fenestration properties.

Properties designated based on `REFERENCE BUILDING WINDOW GLAZING TYPE`
and `REFERENCE BUILDING WINDOW COATED` from the underlying AmBIENCe data,
using EN ISO 52016-1:2017 Tables B.42 and B.43 for the values.


## structure_types.csv

Contains assumed `structure_type` properties.

Maps to the corresponding structures in the underlying AmBIENCe data,
and translates almost directly to `data/structure_type.csv`.


## ventilation.csv

Contains assumed ventilation properties.

>[!CAUTION]
>The underlying datasets unfortunately don't contain ventilation-related
>parameters at all, and are replaced with zeroes.
>In principle, defaults from e.g. [TABULA](https://episcope.eu/welcome/)
>or simular could be used in the future.