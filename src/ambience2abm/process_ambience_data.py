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
        self.data = pd.merge(  # Merge the data together to make it easier to deal with.
            pd.read_excel(building_stock_properties_path),
            pd.read_excel(
                building_stock_heatsys_path, skiprows=[0]
            ),  # Skip first row of header, later headers will be omitted through inner join.
            left_on="REFERENCE BUILDING CODE",
            right_on="Building typology",
        )
        self.data[
            "building_period"
        ] = self.data[  # Create and add `building_period` to avoid dealing with it all the time.
            [
                "REFERENCE BUILDING CONSTRUCTION YEAR LOW",
                "REFERENCE BUILDING CONSTRUCTION YEAR HIGH",
            ]
        ].apply(
            lambda row: "-".join(row.values.astype(str)), axis=1
        )
        self.structure_types = pd.read_csv(structure_types_path).set_index(
            "structure_type"
        )
        self.building_stocks = pd.read_csv(building_stock_path).set_index(
            "building_stock"
        )
        self.building_type_mappings = pd.read_csv(
            building_type_mappings_path
        ).set_index("building_type")
        self.interior_node_depth = interior_node_depth
        self.period_of_variations = period_of_variations
        self.building_stock_statistics = self.calculate_building_stock_statistics()

    def building_periods(self):
        """
        Process the unique building periods from the data.

        Returns
        -------
        building_periods_df
            a DataFrame for building_period.csv export.
        """
        return (
            self.data[
                [
                    "building_period",
                    "REFERENCE BUILDING CONSTRUCTION YEAR LOW",
                    "REFERENCE BUILDING CONSTRUCTION YEAR HIGH",
                ]
            ]
            .rename(
                columns={
                    "REFERENCE BUILDING CONSTRUCTION YEAR LOW": "period_start",
                    "REFERENCE BUILDING CONSTRUCTION YEAR HIGH": "period_end",
                }
            )
            .set_index("building_period")
            .drop_duplicates()
        )

    def calculate_building_stock_statistics(self):
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
                    self.building_type_mappings.loc[
                        r["REFERENCE BUILDING USE CODE"], "building_stock"
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
