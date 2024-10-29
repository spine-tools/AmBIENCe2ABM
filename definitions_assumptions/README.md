# AmBIENCe2ABM/definitions_assumptions

Contains data assumptions required for processing the example archetype building definitions.

This data package is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
as indicated by the master `README.md`.
See brief explanations of the contents below:


## building_fabrics_and_nodes.csv

Assumed configuration of the `building_fabrics`.

Essentially defines the configuration of the simplified lumped-capacitance
building thermal model for the archetype buildings.
Translates directly into `definitions/building_fabrics.csv`.


## building_nodes_and_structures.csv

Assumed configuration of `structure_type`s on `building_node`s.

Translates directly into `definitions/building_node__structure_type.csv`.


## country_loads_mapping.csv

Maps countries to their respective timezones and assumed load and heating profiles.

In essence, "Nordic" countries including DK, EE, FI, LT, LV, NO, and SE are
assumed to use the `nordic` profiles, while the rest of the countries use
the `central` profiles.


## loads_and_set_points.csv

Assumed daily domestic hot water, internal heat gain,
and heating/cooling set point profiles.

Domestic hot water demand profile based on EN 12831-3:2017 Annex B,
assumed to be identical across all countries and building types due to
lack of better data.

Internal heat gain profiles based on EN 16798-1:2019 Annex C
for residential and nonresidential buildings respectively.
Range of heating set points also based on EN 16798-1:2019 Annex C,
but the daily profile estimated loosely based on:

>Ruhnau, O., Hirth, L. & Praktiknjo, A. Time series of heat demand and heat pump efficiency for energy system modeling. Sci Data 6, 189 (2019). https://doi.org/10.1038/s41597-019-0199-y

Cooling set points assumed constant to avoid excessive peaking of cooling demand.