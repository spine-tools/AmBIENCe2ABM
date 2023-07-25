# process_ambience_data.py

# Classes and methods for processing the AmBIENCe datasets.

import pandas as pd
from itertools import product


class AmBIENCeDataset:
    """An object class for containing and processing the raw AmBIENCe data."""

    def __init__(
        self,
        building_stock_properties_path="ambience_data/AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx",
        building_stock_heatsys_path="ambience_data/AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx",
        structure_types_path="assumptions/structure_types.csv",
        building_stock_path="assumptions/building_stock.csv",
        building_type_mappings_path="assumptions/building_type_mappings.csv",
    ):
        """
        Read the AmBIENCe project raw data and assumptions.

        Parameters
        ----------
        building_stock_properties_path : str
            path to the 'AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx' raw data file.
        building_stock_heatsys_path : str
            path to the 'AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx' raw data file.
        structure_types_path : str
            path to the 'structure_types.csv' containing assumptions regarding the properties of different structure types.
        building_stock_path : str
            path to the 'building_stock.csv' containing definitions for the required building stock object.
        building_type_mappings_path : str
            path to the `building_type_mappings.csv` containing building type to building stock mappings.
        """
        self.data = pd.merge(
            pd.read_excel(building_stock_properties_path),
            pd.read_excel(
                building_stock_heatsys_path, skiprows=[0]
            ),  # Skip first row of header, later headers will be omitted through inner join.
            left_on="REFERENCE BUILDING CODE",
            right_on="Building typology",
        )
        self.structure_types = pd.read_csv(structure_types_path)
        self.building_stocks = pd.read_csv(building_stock_path)
        self.building_type_mappings = self.map_building_type_to_stock(
            building_type_mappings_path
        )

    def map_building_type_to_stock(self, building_type_mappings_path):
        """
        Create a dictionary mapping building types to their corresponding building stocks.

        Parameters
        ----------
        building_type_mappings_path : str
            path to the `building_type_mappings.csv` containing building type to building stock mappings.

        Returns
        -------
        building_type_mappings
            a Dictionary mapping building types to building stocks.
        """
        bt2bs = pd.read_csv(building_type_mappings_path)
        return {
            k: v
            for (k, v) in zip(
                *[bt2bs[col] for col in ["building_type", "building_stock"]]
            )
        }

    def map_structure_types(self):
        """
        Map ABM structure types to their AmBIENCe counterparts.

        Returns
        -------
        st_map
            a Dictionary mapping ABM structure types to their AmBIENCe counterparts.
        """
        return {
            k: v
            for (k, v) in zip(
                *[self.structure_types[col] for col in ["structure_type", "mapping"]]
            )
        }

    def building_periods(self):
        """
        Process the unique building periods from the data.

        Returns
        -------
        building_periods_df
            a DataFrame for building_period.csv export.
        """
        bps = pd.unique(
            list(
                zip(
                    *[
                        self.data[col]
                        for col in [
                            "REFERENCE BUILDING CONSTRUCTION YEAR LOW",
                            "REFERENCE BUILDING CONSTRUCTION YEAR HIGH",
                        ]
                    ]
                )
            )
        )
        return pd.DataFrame(
            [["-".join([str(p[0]), str(p[1])]), p[0], p[1]] for p in bps],
            columns=["building_period", "period_start", "period_end"],
        )

    def building_stock_statistics(self):
        """
        Process the basic building stock statistics from data for ArchetypeBuildingModel.jl.

        Returns
        -------
        building_stock_statistics_df
            a DataFrame for building_stock_statistics.csv export.
        """
        bss = pd.DataFrame(  # Form the basic structure.
            [
                [
                    self.building_type_mappings[
                        r["REFERENCE BUILDING USE CODE"]
                    ],  # Building stock from building type mapping
                    r[
                        "REFERENCE BUILDING USE CODE"
                    ],  # Building type directly from data
                    "-".join(
                        [
                            str(r["REFERENCE BUILDING CONSTRUCTION YEAR LOW"]),
                            str(r["REFERENCE BUILDING CONSTRUCTION YEAR HIGH"]),
                        ]
                    ),  # Parse building period from low and high years
                    r[
                        "REFERENCE BUILDING COUNTRY CODE"
                    ],  # Location ID from country code.
                    r[" ".join([hs, "FUEL USED"])],  # Heating system fuel from data.
                    r["NUMBER OF REFERENCE BUILDINGS IN THE BUILDING STOCK SEGMENT"]
                    * r[
                        " ".join([hs, "PREVALENCY ON BUILDING STOCK"])
                    ],  # Multiply number of buildings by heat source prevalency.
                    r[
                        "REFERENCE BUILDING USEFUL FLOOR AREA (m2)"
                    ],  # Useful floor area estimated to be roughly equivalent to gross-floor area.
                ]
                for ((i, r), hs) in product(
                    self.data.iterrows(),
                    ["HEATING SYSTEM 1", "HEATING SYSTEM 2", "HEATING SYSTEM 3"],
                )
            ],
            columns=[
                "building_stock",
                "building_type",
                "building_period",
                "location_id",
                "heat_source",
                "number_of_buildings",
                "average_gross_floor_area_m2_per_building",
            ],
        )
        return (
            bss.dropna()  # Drop NaN rows with invalid heating system data.
            .groupby(  # Group by the actual dimensions...
                [
                    "building_stock",
                    "building_type",
                    "building_period",
                    "location_id",
                    "heat_source",
                ]
            )
            .agg(  # ... and aggregate over the different structural classes in the raw data.
                {
                    "number_of_buildings": "sum",
                    "average_gross_floor_area_m2_per_building": "mean",
                }
            )
        )

    def calculate_structure_effective_thermal_mass(
        self,
        structure_type,
        period_of_variations,
    ):
        """
        Calculate the effective thermal mass according to 'EN ISO 13786:2017 Annex C.2.4' effective thickness method.

        Parameters
        ----------
        thermal_mass : float
            the raw structural thermal mass of the
        """


class ABMDataset:
    """An object class for containing and exporting ArchetypeBuildingModel.jl compatible data."""

    def __init__(self, ambience_data):
        """
        Process the AmBIENCe project raw data for ArchetypeBuildingModel.jl.

        Parameters
        ----------

        """
