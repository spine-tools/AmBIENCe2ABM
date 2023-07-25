# process_ambience_data.py

# Classes and methods for processing the AmBIENCe datasets.

import pandas as pd
import numpy as np
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
        interior_node_depth=0.1,
        period_of_variations=2225140,
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
        interior_node_depth : float
            assumed depth of the aggregated effective thermal mass within the structures, given as a fraction of the total thermal resistance from the indoor surface to the middle of the thermal insulation.
        period_of_variations : float
            assumed period of variations in seconds for the 'EN ISO 13786:2017 Annex C.2.4 Effective thickness method'.
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
                    r["building_period"],  # Fetch building period.
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

    def calculate_weighted_effective_thermal_mass(
        self,
        r,
        st,
        agg_bss,
    ):
        """
        Calculate the effective thermal mass according to 'EN ISO 13786:2017 Annex C.2.4 effective thickness method'.

        Uses a normalized weight for the thermal mass to account for potential
        different structure classes in the AmBIENCe data.

        Parameters
        ----------
        r : DataFrame
            row of the raw AmBIENCe data used for the calculations.
        st : str
            the ABM structure type currently being processed.
        agg_bss : DataFrame
            aggregated building stock statistics for calculating proper normalized weights.

        Returns
        -------
        effective_thermal_mass_J_m2K
        """
        index_tuple = (
            r["REFERENCE BUILDING USE CODE"],  # Building type equals the use code.
            r["building_period"],
            r["REFERENCE BUILDING COUNTRY CODE"],
        )
        # Calculate the weight from the current total floor area vs the total aggregated floor area.
        weight = (
            r["REFERENCE BUILDING USEFUL FLOOR AREA (m2)"]
            * r["NUMBER OF REFERENCE BUILDINGS IN THE BUILDING STOCK SEGMENT"]
        ) / (
            agg_bss.loc[index_tuple, "number_of_buildings"]
            * agg_bss.loc[index_tuple, "average_gross_floor_area_m2_per_building"]
        )
        # Calculate the total specific heat capacity per structure area up until the middle of the insulation.
        pretext = " ".join(
            ["REFERENCE BUILDING", self.structure_types.loc[st, "mapping"]]
        )
        shc = (
            r[" ".join([pretext, "MATERIAL THICKNESS (m)"])]
            * r[" ".join([pretext, "MATERIAL DENSITY (kg/m3)"])]
            * r[" ".join([pretext, "MATERIAL SPECIFIC HEAT CAPACITY (J/kg/K)"])]
            + (not self.structure_types.loc[st, "is_internal"])
            * 0.5
            * r[" ".join([pretext, "INSULATION MATERIAL THICKNESS (m)"])]
            * r[" ".join([pretext, "INSULATION MATERIAL DENSITY (kg/m3)"])]
            * r[
                " ".join(
                    [pretext, "INSULATION MATERIAL SPECIFIC HEAT CAPACITY (J/kg/K)"]
                )
            ]
        )
        # Apply the period of variations according to 'EN ISO 13786:2017 Annex C.2.4 effective thickness method'
        return np.sqrt(
            shc**2
            / (
                1
                + (2 * np.pi / self.period_of_variations) ** 2
                * shc**2
                * self.structure_types.loc[st, "interior_resistance_m2K_W"] ** 2
            )
        )


class ABMDataset:
    """An object class for containing and exporting ArchetypeBuildingModel.jl compatible data."""

    def __init__(self, ambience_data):
        """
        Process the AmBIENCe project raw data for ArchetypeBuildingModel.jl.

        Parameters
        ----------

        """
