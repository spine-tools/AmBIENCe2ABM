## AmBIENCe2ABM/data_sources/eurostat

Contains [NUTS country shapefiles from Eurostat](https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics).

The original shapefile from the above website includes all countries in a single file.
However, for [ArchetypeBuildingModel.jl](https://github.com/vttresearch/ArchetypeBuildingModel),
it is preferred to have them country-by-country to avoid excessive weather data processing.

While the [license](https://ec.europa.eu/eurostat/web/main/help/copyright-notice)
for the re-publishing is not clear, non-commercial use of this data is permitted as long
as the source is acknowledged.


## Acknowledgements

>[Territorial units for statistics (NUTS)](https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics),
>accessed 2024-10-11.
>© EuroGeographics for the administrative boundaries.