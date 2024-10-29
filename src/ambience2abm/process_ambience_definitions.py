# process_ambience_definitions.py

# Classes and methods for processing AmBIENCe archetype building definitions.

import pandas as pd
import numpy as np
from . import __version__
from frictionless import Package
from datetime import datetime


class ABMDefinitions:
    """An object class for processing and containing AmBIENCe archetype building definitions."""

    def __init__(
        self,
        ambience,
        building_fabrics_path="definitions_assumptions/building_fabrics_and_nodes.csv",
        building_nodes_path="definitions_assumptions/building_nodes_and_structures.csv",
        loads_mapping_path="definitions_assumptions/country_loads_mapping.csv",
        loads_path="definitions_assumptions/loads_and_set_points.csv",
        room_height_m=2.6,
        weather_start="2016-01-01",
        weather_end="2016-01-02",
        partition_wall_length_ratio_to_external_walls_m_m=0.5,
        window_area_thermal_bridge_surcharge_W_m2K=0.1,
        aggregate_building_type=True,
        aggregate_building_period=True,
    ):
        """
        Process and store AmBIENCe archetype building definitions.

        Parameters
        ----------
        ambience : AmBIENCeDataset
            the pre-processed AmBIENCe project raw dataset.
        building_fabrics_path : str
            path to a .csv file containing assumptions regarding the building RC-model structure.
        building_nodes_path : str
            path to a .csv file containing assumed lumped-capacitance node configuration.
        loads_mapping_path : str
            path to a .csv file mapping countries to timezones and load/setpoint profiles.
        loads_path : str
            path to a .csv file defining domestic hot water, internal heat gains, and heating/cooling set point profiles.
        room_height_m : float
            assumed height of rooms/storeys in metres, default based on AmBIENCe `D4.1 Database of grey-box model parameter values for EU building typologies`.
        weather_start : datetime-like str
            Desired `weather_start` parameter for the archetypes, required for ABM.jl.
        weather_end : datetime_like_str
            Desired `weather_end` parameter for the archetypes, required for ABM.jl.
        partition_wall_length_ratio_to_external_walls_m_m : float
            Assumed length of partition walls relative to the exterior walls, default 0.5 based on AmBIENCe.
        window_area_thermal_bridge_surcharge_W_m2K : float
            Assumed thermal bridging of windows, default 0.1 based on TABULA.
        aggregate_building_type : bool
            Flag to aggregate building types according to "data_assumptions/building_type_mappings.csv".
        aggregate_building_period : bool
            Flag to aggregate all periods.
        """
        self.ambience = ambience
        self.room_height_m = room_height_m
        self.weather_start = weather_start
        self.weather_end = weather_end
        self.partition_wall_length_ratio_to_external_walls_m_m = (
            partition_wall_length_ratio_to_external_walls_m_m
        )
        self.window_area_thermal_bridge_surcharge_W_m2K = (
            window_area_thermal_bridge_surcharge_W_m2K
        )
        self.building_fabrics = pd.read_csv(building_fabrics_path).set_index(
            "building_node"
        )
        self.building_node__structure_type = pd.read_csv(building_nodes_path).set_index(
            "structure_type"
        )
        self.loads_mapping = pd.read_csv(loads_mapping_path).set_index("country")
        self.loads = pd.read_csv(loads_path)
        self.data = self.preprocess_data(
            aggregate_building_type,
            aggregate_building_period,
        )
        self.loads_data = self.preprocess_loads()

    def preprocess_data(
        self,
        aggregate_building_type,
        aggregate_building_period,
    ):
        """
        Preprocess AmBIENCe data for archetype building definitions.

        Parameters
        ----------
        aggregate_building_type : bool
            Flag to aggregate building types according to "data_assumptions/building_type_mappings.csv".
        aggregate_building_period : bool
            Flag to aggregate all periods.

        Returns
        -------
        df : DataFrame
            DataFrame containing the preprocessed AmBIENCe data.
        """
        # Fetch and rename relevant data from ambience
        cols = {
            "building_stock": "building_stock",
            "location_id": "location_id",
            "building_type": "building_type",
            "building_period": "building_period",
            "number_of_buildings": "number_of_buildings",
            "average_gross_floor_area_m2_per_building": "average_gross_floor_area_m2_per_building",
            "category": "category",
            "NUMBER OF REFERENCE BUILDING STOREYS": "number_of_storeys",
            "REFERENCE BUILDING GROUND FLOOR AREA (m2)": "reference_floor_area_m2",
            "REFERENCE BUILDING WALL AREA (m2)": "reference_wall_area_m2",
            "REFERENCE BUILDING WINDOW AREA (m2)": "reference_window_area_m2",
            "REFERENCE BUILDING ROOF AREA (m2)": "reference_roof_area_m2",
            "HEATING SYSTEM 1 HEAT SOURCE": "heat_source_1",
            "HEATING SYSTEM 2 HEAT SOURCE": "heat_source_2",
            "HEATING SYSTEM 3 HEAT SOURCE": "heat_source_3",
            "REFERENCE BUILDING CONSTRUCTION YEAR LOW": "period_low",
            "REFERENCE BUILDING CONSTRUCTION YEAR HIGH": "period_high",
        }
        df = self.ambience.data[cols.keys()].reset_index()
        df = df.rename(columns=cols)
        # Calculate max and min period years
        agg_df = df.groupby(["location_id"]).agg(
            min_period_year=("period_low", "min"),
            max_period_year=("period_high", "max"),
        )
        df = df.join(agg_df, on="location_id")
        # Form scope building type id
        if aggregate_building_type:
            df["scope_types"] = df["category"]
        else:
            df["scope_types"] = df["building_type"]
        # Form scope period start and end years
        if aggregate_building_period:
            df["scope_period_start_year"] = df["min_period_year"]
            df["scope_period_end_year"] = df["max_period_year"]
        else:
            df["scope_period_start_year"] = df["period_low"]
            df["scope_period_end_year"] = df["period_high"]
        # Form `building_scope` names
        df["building_scope"] = (
            df["location_id"]
            + "_"
            + df["scope_types"]
            + "_"
            + df["scope_period_start_year"].apply(str)
            + "_"
            + df["scope_period_end_year"].apply(str)
        )
        # Calculate reference building weights by `building_scope`
        df["total_gross_floor_area_m2"] = (
            df["number_of_buildings"] * df["average_gross_floor_area_m2_per_building"]
        )
        agg_df = df.groupby(["building_scope"]).agg(
            total_gross_floor_area_m2_per_scope=("total_gross_floor_area_m2", "sum")
        )
        df = df.join(agg_df, on="building_scope")
        df["weight_within_scope"] = (
            df["total_gross_floor_area_m2"] / df["total_gross_floor_area_m2_per_scope"]
        )
        # Join timezones and load mappings
        df = df.join(self.loads_mapping, on="location_id")
        # Form `building_loads` id
        df["building_loads"] = (
            df["loads"] + "_" + df["category"] + "_UTC+" + df["timezone"].apply(str)
        )
        return df

    def preprocess_loads(self):
        """
        Create the necessary timezoned building_loads.

        Returns
        -------
        df : DataFrame
            Preprocessed building loads data.
        """
        # Figure out the load categories and timeseries
        df1 = self.loads_mapping.reset_index()[["timezone", "loads"]].drop_duplicates()
        df2 = self.loads.reset_index()[["loads", "category"]].drop_duplicates()
        df = df1.join(df2.set_index("loads"), on="loads")
        # Form the full timezoned loads
        df = self.loads.join(df.set_index("loads")[["timezone"]], on="loads")
        df["hour"] = (df["hour"] - df["timezone"]) % 24
        df["hours"] = (
            "h"
            + df["hour"].apply(str).str.zfill(2)
            + "-"
            + (df["hour"] + 1).apply(str).str.zfill(2)
        )
        # Form `building_loads` id
        df["building_loads"] = (
            df["loads"] + "_" + df["category"] + "_UTC+" + df["timezone"].apply(str)
        )
        # Reorganize
        df = (
            df[
                [
                    "building_loads",
                    "loads",
                    "category",
                    "timezone",
                    "hour",
                    "hours",
                    "domestic_hot_water_demand_gfa_scaling_W_m2",
                    "internal_heat_loads_gfa_scaling_W_m2",
                    "indoor_air_heating_set_point_override_K",
                    "indoor_air_cooling_set_point_override_K",
                ]
            ]
            .drop_duplicates()
            .set_index("building_loads")
            .sort_index()
            .sort_values(by=["loads", "category", "timezone", "hour"])
        )
        return df.drop_duplicates()

    def calculate_building_frame_depth(self, df, rounding=2):
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
        A_facade = df["reference_wall_area_m2"] + df["reference_window_area_m2"]
        A_floor = df["reference_floor_area_m2"]
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
        df["window_area_to_external_wall_ratio_m2_m2"] = df[
            "reference_window_area_m2"
        ] / (df["reference_window_area_m2"] + df["reference_wall_area_m2"])
        return df

    def building_scope(self):
        """
        Gather `building_scope` for .csv export.

        Returns
        -------
        df : DataFrame
            A dataframe with unique building scopes and their parameters.
        """
        return (
            self.data[
                [
                    "building_scope",
                    "building_stock",
                    "scope_period_start_year",
                    "scope_period_end_year",
                ]
            ]
            .drop_duplicates()
            .set_index("building_scope")
        )

    def building_scope__building_type(self):
        """
        Gather `building_scope`-`building_stock`-pairs for .csv export.

        Returns
        -------
        df : DataFrame
            A dataframe linking `building_scope`s to their included `building_types`s.
        """
        return (
            self.data[["building_scope", "building_type"]]
            .drop_duplicates()
            .set_index("building_scope")
        )

    def building_scope__heat_source(self):
        """
        Map heat sources to building scopes for .csv export

        Returns
        -------
        df : DataFrame
            a dataframe mapping heat sources to building scopes.
        """
        cols = ["building_stock", "building_type", "building_period", "location_id"]
        bss = (
            self.ambience.calculate_building_stock_statistics()
            .reset_index()
            .set_index(cols)["heat_source"]
        )
        df = self.data.set_index(cols)
        df = df.join(bss).reset_index()
        return (
            df[["building_scope", "heat_source"]]
            .drop_duplicates()
            .set_index("building_scope")
        )

    def building_scope__location_id(self):
        """
        Map location ids to building scopes for .csv export.

        Returns
        -------
        df : DataFrame
            a dataframe mapping location ids to building scopes.
        """
        return (
            self.data[["building_scope", "location_id"]]
            .drop_duplicates()
            .set_index("building_scope")
        )

    def building_archetype(self):
        """
        Compile building archetype data for .csv export.

        Returns
        -------
        df : DataFrame
            Preprocessed definitions related data.
        """
        df = self.data.copy()
        # Add `building_fabrics`.
        df["building_fabrics"] = self.building_fabrics["building_fabrics"].unique()[0]
        # Add assumed archetype parameters
        df["weather_start"] = self.weather_start
        df["weather_end"] = self.weather_end
        df["partition_wall_length_ratio_to_external_walls_m_m"] = (
            self.partition_wall_length_ratio_to_external_walls_m_m
        )
        df["window_area_thermal_bridge_surcharge_W_m2K"] = (
            self.window_area_thermal_bridge_surcharge_W_m2K
        )
        df["room_height_m"] = self.room_height_m
        # Calculate archetype building properties of interest
        df = self.calculate_building_frame_depth(df)
        df = self.calculate_window_area_to_external_wall_ratio_m2_m2(df)
        # Prep weighted properties within scope.
        cols = [
            "building_frame_depth_m",
            "number_of_storeys",
            "window_area_to_external_wall_ratio_m2_m2",
            "reference_floor_area_m2",
            "reference_wall_area_m2",
            "reference_window_area_m2",
            "reference_roof_area_m2",
        ]
        weighted_df = (
            df[cols]
            .apply(lambda col: col * df["weight_within_scope"])
            .rename(columns={col: "weighted_" + col for col in cols})
        )
        df = df.join(weighted_df)
        # Add `building_archetype` dimension and aggregate over it.
        df["building_archetype"] = df["building_scope"]
        agg_df = df.groupby(["building_archetype"]).agg(
            {"weighted_" + col: ["sum"] for col in cols}
        )
        agg_df = agg_df.droplevel(1, axis=1).rename(
            columns={"weighted_" + col: col for col in cols}
        )
        df = df.set_index("building_archetype")
        agg_df = agg_df.join(df, rsuffix="_old")
        # Round `number_of_storeys` to the nearest 0.5 to avoid excessive partial storeys.
        agg_df["number_of_storeys"] = round(agg_df["number_of_storeys"] * 2) / 2
        # Reorder columns and return
        return agg_df[
            [
                "building_scope",
                "building_fabrics",
                "building_frame_depth_m",
                "number_of_storeys",
                "weather_start",
                "weather_end",
                "room_height_m",
                "window_area_to_external_wall_ratio_m2_m2",
                "partition_wall_length_ratio_to_external_walls_m_m",
                "window_area_thermal_bridge_surcharge_W_m2K",
                "reference_floor_area_m2",
                "reference_wall_area_m2",
                "reference_window_area_m2",
                "reference_roof_area_m2",
            ]
        ].drop_duplicates()

    def building_loads(self):
        """
        Compile building loads definitions for export

        Returns
        -------
        df : DataFrame
            Processed building_loads definitions.
        """
        return self.loads_data[
            [
                "hours",
                "domestic_hot_water_demand_gfa_scaling_W_m2",
                "internal_heat_loads_gfa_scaling_W_m2",
            ]
        ]

    def building_archetype__building_loads(self):
        """
        Connect archetype buildings to their respective loads and set points.

        Returns
        -------
        df : DataFrame
            Processed archetype_building__building_loads definitions.
        """
        df = self.loads_data.join(
            self.data.set_index("building_loads")["building_scope"]
        ).rename(columns={"building_scope": "building_archetype"})
        return (
            df.reset_index()[
                [
                    "building_archetype",
                    "building_loads",
                    "hours",
                    "indoor_air_heating_set_point_override_K",
                    "indoor_air_cooling_set_point_override_K",
                ]
            ]
            .drop_duplicates()
            .set_index("building_archetype")
        )

    def export_csvs(self, folderpath="definitions/"):
        """
        Sort and export the ABMDefinitions contents as .csv files.

        Parameters
        ----------
        folderpath : str
            the folder path where to export the contents.

        Returns
        -------
        a bunch of .csv files as output, but the function returns nothing.
        """
        self.building_archetype().sort_index().to_csv(
            folderpath + "building_archetype.csv"
        )
        self.building_scope().sort_index().to_csv(folderpath + "building_scope.csv")
        self.building_scope__building_type().sort_index().to_csv(
            folderpath + "building_scope__building_type.csv"
        )
        self.building_scope__heat_source().sort_index().to_csv(
            folderpath + "building_scope__heat_source.csv"
        )
        self.building_scope__location_id().sort_index().to_csv(
            folderpath + "building_scope__location_id.csv"
        )
        self.building_fabrics.sort_index().to_csv(folderpath + "building_fabrics.csv")
        self.building_node__structure_type.sort_index().to_csv(
            folderpath + "building_node__structure_type.csv"
        )
        self.building_loads().to_csv(folderpath + "building_loads.csv")
        self.building_archetype__building_loads().to_csv(
            folderpath + "building_archetype__building_loads.csv"
        )

    def create_datapackage(self, folderpath="definitions/"):
        """
        Create and infer a DataPackage from exported .csv files.

        Parameters
        ----------
        folderpath : str
            the folder path of the DataPackage contents.

        Returns
        -------
        pkg
            a Package object with contents and metadata.
        """
        pkg = Package(folderpath + "*.csv")
        pkg.infer()
        pkg.name = "ambience2abm_definitions"
        pkg.licenses = [
            {
                "name": "CC-BY-4.0",
                "path": "https://creativecommons.org/licenses/by/4.0/",
                "title": "Creative Commons Attribution 4.0",
            }
        ]
        pkg.profile = "data-package"
        pkg.title = "AmBIENCe2ABM reference building definitions"
        pkg.description = "A reference building definition package processed from AmBIENCe project EU27 data for use with ArchetypeBuildingModel.jl."
        pkg.homepage = "https://github.com/spine-tools/AmBIENCe2ABM.jl"
        pkg.version = __version__
        pkg.sources = [
            {
                "name": "D4.1 Database of grey-box model parameter values for EU building typologies",
                "web": "https://ambience-project.eu/wp-content/uploads/2022/02/AmBIENCe_D4.1_Database-of-grey-box-model-parameter-values-for-EU-building-typologies-update-version-2-submitted.pdf",
            },
            {
                "name": "Database of grey-box model parameters",
                "web": "https://ambience-project.eu/wp-content/uploads/2022/03/AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx",
            },
            {
                "name": "D4.2 - Buildings Energy Systems Database EU27",
                "web": "https://ambience-project.eu/wp-content/uploads/2022/06/AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx",
            },
        ]
        pkg.contributors = [
            {
                "title": "Topi Rasku",
                "email": "topi.rasku@vtt.fi",
                "path": "https://cris.vtt.fi/en/persons/topi-rasku",
                "role": "author",
                "organization": "VTT Technical Research Centre of Finland Ltd",
            }
        ]
        pkg.keywords = [
            "European Union",
            "EU",
            "Building stock",
            "Building structures",
            "Fenestration",
            "Construction",
            "AmBIENCe",
            "Mopo",
            "Hotmaps",
            "ABM.jl",
            "ArchetypeBuildingModel.jl",
        ]
        pkg.created = datetime.today().isoformat()
        return pkg
