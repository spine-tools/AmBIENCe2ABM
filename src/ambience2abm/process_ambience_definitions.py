# process_ambience_definitions.py

# Classes and methods for processing AmBIENCe archetype building definitions.

import pandas as pd
import numpy as np


class ABMDefinitions:
    """An object class for processing and containing AmBIENCe archetype building definitions."""

    def __init__(
        self,
        ambience,
        building_fabrics_path="definitions_assumptions/building_fabrics_and_nodes.csv",
        building_nodes_path="definitions_assumptions/building_nodes_and_structures.csv",
        room_height_m=2.6,
    ):
        """
        Process and store AmBIENCe archetype building definitions.

        Parameters
        ----------
        ambience : AmBIENCeDataset
            the pre-processed AmBIENCe project raw dataset.
        building_fabrics_path : str
            path to a .csv file containing assumptions regarding the building RC-model structure.
        room_height_m : float
            assumed height of rooms/storeys in metres, default based on AmBIENCe `D4.1 Database of grey-box model parameter values for EU building typologies`.
        """
        self.room_height_m = room_height_m
        self.building_fabrics = pd.read_csv(building_fabrics_path).set_index(
            "building_node"
        )
        self.building_node__structure_type = pd.read_csv(building_nodes_path).set_index(
            "structure_type"
        )
        self.building_archetype = self.calculate_building_archetype(ambience)
        self.building_scope = self.calculate_building_scope(ambience)

    def calculate_building_frame_depth(self, df):
        """
        Calculates the building frame depth in metres based on the given exterior dimensions.

        Parameters
        ----------
        df : DataFrame
            a pre-processed building archetype dataframe.

        Returns
        -------
        df : DataFrame
            the same dataframe with an added column for the building frame depth.
        """
        A_facade = df["wall_area_m2"] + df["window_area_m2"]
        A_floor = df["floor_area_m2"]
        nh = df["number_of_storeys"] * self.room_height_m
        df["building_frame_depth_m"] = (
            A_facade / 2 / nh - np.sqrt((A_facade / 2 / nh) ** 2 - 4 * A_floor)
        ) / 2
        # AmBIENCe assumes a fixed external wall ratio of 1.5 if not computable.
        df.loc[df["building_frame_depth_m"].isna(), "building_frame_depth_m"] = np.sqrt(
            A_floor / 1.5
        )
        return df

    def calculate_window_area_to_external_wall_ratio_m2_m2(self, df):
        """
        Calculates the window area to external wall ratio.

        Parameters
        ----------
        df : DataFrame
            a pre-processed building archetype dataframe

        Returns
        -------
        df : DataFrame
            the same dataframe with an added column for the window-to-wall ratio
        """
        df["window_area_to_external_wall_ratio_m2_m2"] = df["window_area_m2"] / (
            df["window_area_m2"] + df["wall_area_m2"]
        )
        return df

    def calculate_building_archetype(self, ambience):
        """
        Calculate building archetype data.

        Parameters
        ----------
        ambience : AmBIENCeDataset
            the pre-processed AmBIENCe dataset.

        Returns
        -------
        df : DataFrame
            Preprocessed definitions related data.
        """
        # Renaming columns
        cols = {
            "REFERENCE BUILDING CODE": "building_archetype",
            "REFERENCE BUILDING COUNTRY CODE": "location_id",
            "REFERENCE BUILDING USE CODE": "building_type",
            "building_period": "building_period",
            "NUMBER OF REFERENCE BUILDING STOREYS": "number_of_storeys",
            "REFERENCE BUILDING GROUND FLOOR AREA (m2)": "floor_area_m2",
            "REFERENCE BUILDING WALL AREA (m2)": "wall_area_m2",
            "REFERENCE BUILDING WINDOW AREA (m2)": "window_area_m2",
            "REFERENCE BUILDING ROOF AREA (m2)": "roof_area_m2",
        }
        df = ambience.data.reset_index().rename(columns=cols)
        df = df[cols.values()].set_index("building_archetype")

        # Add `building_scope`.
        df["building_scope"] = [
            "-".join([r["location_id"], r["building_type"], r["building_period"]])
            for (i, r) in df.iterrows()
        ]

        # Add `building_fabrics`.
        df["building_fabrics"] = self.building_fabrics["building_fabrics"].unique()[0]

        # Calculate archetype building properties of interest
        df["room_height_m"] = self.room_height_m
        df = self.calculate_building_frame_depth(df)
        df = self.calculate_window_area_to_external_wall_ratio_m2_m2(df)

        # Reorder columns
        df = df[
            [
                "building_scope",
                "building_fabrics",
                "building_frame_depth_m",
                "number_of_storeys",
                "room_height_m",
                "window_area_to_external_wall_ratio_m2_m2",
                "floor_area_m2",
                "wall_area_m2",
                "window_area_m2",
                "roof_area_m2",
            ]
        ]
        return df

    def calculate_building_scope(self, ambience):
        """
        Calculate the building scopes and parameters

        Parameters
        ----------
        ambience : AmBIENCeDataset
            the perprocessed AmBIENCe data.

        Returns
        -------
        df : DataFrame
            a dataframe with unique building scopes and their parameters.
        """
        cols = {
            "REFERENCE BUILDING COUNTRY CODE": "location_id",
            "REFERENCE BUILDING USE CODE": "building_type",
            "building_period": "building_period",
            "REFERENCE BUILDING CONSTRUCTION YEAR LOW": "scope_period_start_year",
            "REFERENCE BUILDING CONSTRUCTION YEAR HIGH": "scope_period_end_year",
        }
        df = ambience.data.rename(columns=cols)
        df = df[cols.values()]
        # Form building scope name
        df["building_scope"] = [
            "-".join([r["location_id"], r["building_type"], r["building_period"]])
            for (i, r) in df.iterrows()
        ]
        # Fetch the corresponding building stock
        df["building_stock"] = [
            ambience.building_type_mappings.loc[r["building_type"], "building_stock"]
            for (i, r) in df.iterrows()
        ]
        # Reorder columns and set index
        df = df.set_index("building_scope").drop_duplicates()
        df = df[
            [
                "location_id",
                "building_type",
                "building_stock",
                "scope_period_start_year",
                "scope_period_end_year",
            ]
        ]
        return df
