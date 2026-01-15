# AmBIENCe2ABM/data

Contains the processed [Data Package](https://specs.frictionlessdata.io//data-package/)
for the building stock data.

This data package is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
as indicated by the master `README.md`.
See brief explanations of the contents below:

>[!IMPORTANT]
>While this dataset might appear quite impressive on the surface,
>a lot of the data is duplicated across dimensions to fit the desired format.
>The data format was originally designed for
>[FinnishBuildingStockData.jl](https://github.com/vttresearch/FinnishBuildingStockData),
>which uses high-quality Finnish building stock data.


## building_period.csv

Contains all the different building periods in the data.

Essentially, this means the timespan during which buildings were built
denoted as a span in years.
Also includes the first and last years of the period in the
`period_start` and `period_end` columns.


## building_stock_statistics.csv

Contains data about the composition of the building stocks,

The most important data file.
Essentially, tells the `number_of_buildings` and
`average_gross_floor_area_m2_per_building` per `building_stock`, `building_type`,
`building_period`, `location_id`, and `heat_source`.


## building_stock.csv

Contains the properties of all the `building_stock` entries in the dataset.

The `building_stock`s are used to group `building_stock_statistics` rows together.
In this dataset, their primary function is to separate countries,
as well as extrapolated data from each other,
since all the building stock data is from the same year.

The `building_stock`s also link to the shapefile and raster information via the
`shapefile_path` and `raster_path` columns, which are used for weather data
aggregation in [ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel).


## location_id.csv

Contains all the `location_id`s in the dataset.

Essentially just an identifier for geographical scopes,
and links to the `location` field in the shapefiles under
`data_sources/eurostat` and `data_sources/natural_earth`.


## structure_statistics.csv

Contains properties of the building envelopes.

The second-most important data file.
Essentially, tells different U-values, effective thermal mass,
as well as linear thermal brige properties per `building_type`,
`building_period`, `location_id`, and `structure_type`.
The `design_U_value_W_m2K` contains data straight from the AmBIENCe
project datasets, while the rest are calculated based on it and the
`--ind` and `--pov` assumptions when the dataset is generated.


## structure_type.csv

Contains definitions for different `structure_type`s.

Additionally, defines some technical properties of each `structure_type`,
such as `interior_resistance_m2K_W` and `exterior_resistance_m2K_W` for
the assumed surface resistances.


## ventilation_and_fenestration_statistics.csv

Contains building stock ventilation and fenestration properties.

The third-most important data file.
Essentially tells the `HRU_efficiency` (ventilation heat recovery unit efficiency),
`infiltration_rate_1_h`, `ventilation_rate_1_h`,
`total_normal_solar_energy_transmittance`, and `window_U_value_W_m2K` per
`building_type`, `building_period`, and `location_id`.

>[!CAUTION]
>The underlying datasets unfortunately don't contain ventilation-related
>parameters at all, and are replaced with zeroes.
>Crude assumption based on [EPISCOPE-TABULA](https://episcope.eu/welcome/)
>are used instead.