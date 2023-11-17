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
args = parser.parse_args()


## Process data, export .csvs and update the datapackages.

print("Processing raw data...")
ambience = amb.AmBIENCeDataset(
    interior_node_depth=args.ind,
    period_of_variations=args.pov,
)
print("Processing ABM data...")
abmdata = amb.ABMDataset(ambience)
print("Exporting data .csvs...")
abmdata.export_csvs()
print("Creating `data.json`...")
abmdata.create_datapackage().to_json("data.json")
print("Processing ABM definitions...")
defs = amb.ABMDefinitions(ambience)
print("Exporting definition .csvs...")
defs.export_csvs()
print("Creating `definitions.json`...")
defs.create_datapackage().to_json("definitions.json")

print("All done!")
