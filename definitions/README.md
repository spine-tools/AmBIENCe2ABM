# # AmBIENCe2ABM/definitions

Contains the processed [Data Package](https://specs.frictionlessdata.io//data-package/)
for [ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel)
example archetype building definitions.
See its documentation for details on the exact nature of each parameter.

This data package is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
as indicated by the master `README.md`.
See brief explanations of the contents below:


## building_archetype__building_loads.csv

Maps example archetype building definitions to their respective building loads
definitions.

Also contains timezoned timepatterns for heating and cooling set points
based on `definitions_assumptions/country_loads_mapping.csv`
and `definitions_assumptions/loads_and_set_points.csv`.


## building_archetype.csv

Contains example archetype building definitions.

Essentially, each `building_archetype` is a single building that is used to
represent all the building stock encompassed by its `building_scope`,
while `building_fabrics` defines how the building model is configured.

Also contains a number of columns defining assumptions related to the
shape of the building envelope, as well as dates for automatic weather
data processing in 
[ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel).


## building_fabrics.csv

Defines the configuration of the simplified lumped-capacitance building
thermal models for the archetype buildings.

Essentially links `building_node`s to `building_fabrics`,
and specifies the `interior_air_and_furniture_weight`.


## building_loads.csv

Contains definitions for building loads.

Essentially, defines daily domestic hot water demand and internal heat gain
demand patterns based on `definitions_assumptions/country_loads_mapping.csv`
and `definitions_assumptions/loads_and_set_points.csv`.


## building_node__structure_type.csv

Defines which `structure_type`s are assigned to which `building_node`s.

Required for calculating the paramters of the simplified lumped-capacitance
building thermal models in
[ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel).


## building_scope__heat_source.csv

Assigns `heat_source`s for `building_scope`s.

In the current example, the `building_scope`s include all available `heat_source`s,
meaning that the archetype buildings using said `building_scope`s represent
average buildings across those `heat_source`s.


## building_scope.csv

Defines the geographical, building typological, and temporal scopes of the desired
archetype buildings.

Essentially assings `location_id`s, `building_type`s, and `building_stock`s to
form a desired `building_scope`, as well as defines the desired time period using
`scope_period_start_year` and `scope_period_end_year`.