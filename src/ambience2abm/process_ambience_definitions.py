# process_ambience_definitions.py

# Classes and methods for processing AmBIENCe archetype building definitions.

import numpy as np


class ABMDefinitions:
    """An object class for processing and containing AmBIENCe archetype building definitions."""

    def __init__(
        self,
        ambience,
        building_fabrics_path="definitions_assumptions/building_fabrics.csv",
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
        self.building_archetype = self.calculate_building_archetype(ambience)

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
        Process building archetypes from AmBIENCe data.

        Parameters
        ----------
        ambience : AmBIENCeDataset
            the pre-processed AmBIENCe dataset.

        Returns
        -------
        df : DataFrame
            the `building_archetype` and `building_scope` definitions.
        """
        # Renaming columns
        cols = {
            "REFERENCE BUILDING CODE": "building_archetype",
            "REFERENCE BUILDING COUNTRY CODE": "location_id",
            "REFERENCE BUILDING USE CODE": "building_type",
            "building_period": "building_period",
            "REFERENCE BUILDING CONSTRUCTION YEAR LOW": "scope_period_start_year",
            "REFERENCE BUILDING CONSTRUCTION YEAR HIGH": "scope_period_end_year",
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

        # Add `building_stock`.
        df["building_stock"] = [
            ambience.building_type_mappings.loc[bt, "building_stock"]
            for bt in df["building_type"]
        ]

        # Calculate archetype building properties of interest
        df["room_height_m"] = self.room_height_m
        df = self.calculate_building_frame_depth(df)
        df = self.calculate_window_area_to_external_wall_ratio_m2_m2(df)

        # Reorder columns
        df = df[
            [
                "building_frame_depth_m",
                "number_of_storeys",
                "room_height_m",
                "window_area_to_external_wall_ratio_m2_m2",
                "floor_area_m2",
                "wall_area_m2",
                "window_area_m2",
                "roof_area_m2",
                "building_scope",
                "building_stock",
                "building_type",
                "heat_source",
                "location_id",
                "scope_period_start_year",
                "scope_period_end_year",
            ]
        ]
