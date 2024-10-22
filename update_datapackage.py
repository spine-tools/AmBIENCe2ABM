# update_datapackage.py

# Main python program to update the datapackage.

import argparse
import ambience2abm as amb


## Create parser for command line

parser = argparse.ArgumentParser(
    prog="update_datapackage.py",
    description="Updates the AmBIENCe2ABM datapackage using the given input arguments.",
)
parser.add_argument(
    "--ind",
    type=float,
    default=0.1,
    help="The assumed depth of the structural temperature nodes, given as a fraction of the total thermal resistance of the structure from its interior surface up to the middle of its insulation (or itself if no insulation). 0.1 by default.",
)
parser.add_argument(
    "--pov",
    type=float,
    default=1209600,
    help="The assumed period of variations in seconds for the 'EN ISO 13786:2017 Annex C.2.4 Effective thickness method' for calculating the effective thermal mass of the structures. 1209600 seconds by default.",
)
parser.add_argument(
    "--extrapolate",
    type=bool,
    default=True,
    help="Trigger extrapolation for countries not in the original data. Customise via `Extrapolation settings` in `update_datapackage.py`.",
)
parser.add_argument(
    "--aggregate_building_type",
    type=bool,
    default=True,
    help="Flag to aggregate archetype building definitions by building type into residential and nonresidential categories.",
)
parser.add_argument(
    "--aggregate_building_period",
    type=bool,
    default=True,
    help="Flag to aggregate all available building periods into a single archetype.",
)
args = parser.parse_args()


## Extrapolation settings

extrapolation_mappings = {
    "SE": ("NO", 0.52),
    "IE": ("UK", 13.26),
    "AT": ("CH", 0.97),
}  # Mapping existing countries to new countries with population-based multipliers.
extrapolation_tag = "ext"  # `building_stock` field pre-pend for new countries.
extrapolation_year = 2016  # `building_stock_year` of new countries.


## Process data, export .csvs and update the datapackages.

print("Processing raw data...")
ambience = amb.AmBIENCeDataset(
    interior_node_depth=args.ind,
    period_of_variations=args.pov,
)
if args.extrapolate:
    print("Extrapolating dataset...")
    ambience.extrapolate(
        mappings=extrapolation_mappings, tag=extrapolation_tag, year=extrapolation_year
    )
print("Processing ABM data...")
abmdata = amb.ABMDataset(ambience)
print("Exporting data .csvs...")
abmdata.export_csvs()
print("Creating `data.json`...")
abmdata.create_datapackage().to_json("data.json")
print("Processing ABM definitions...")
defs = amb.ABMDefinitions(
    ambience,
    aggregate_building_period=args.aggregate_building_period,
    aggregate_building_type=args.aggregate_building_type,
)
print("Exporting definition .csvs...")
defs.export_csvs()
print("Creating `definitions.json`...")
defs.create_datapackage().to_json("definitions.json")

print("All done!")
