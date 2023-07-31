# process_ambience_data.py

# Classes and methods for processing the AmBIENCe datasets.

import pandas as pd
import numpy as np
from . import __version__
from itertools import product
from frictionless import Package
from datetime import datetime


class AmBIENCeDataset:
    """An object class for containing and processing the raw AmBIENCe data."""

    def __init__(
        self,
        building_stock_properties_path="data_sources/ambience/AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx",
        building_stock_heatsys_path="data_sources/ambience/AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx",
        structure_types_path="data_assumptions/structure_types.csv",
        building_stock_path="data_assumptions/building_stock.csv",
        building_type_mappings_path="data_assumptions/building_type_mappings.csv",
        fenestration_path="data_assumptions/fenestration.csv",
        ventilation_path="data_assumptions/ventilation.csv",
        interior_node_depth=0.1,
        period_of_variations=2225140,
        heatsys_skiprows=[0],
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
        fenestration_path : str
            path to the `fenestration.csv` containing assumption regarding fenestration properties.
        ventilation_path : str
            path to the `ventilation.csv` containing assumptions regarding ventilation properties.
        interior_node_depth : float
            assumed depth of the aggregated effective thermal mass within the structures, given as a fraction of the total thermal resistance from the indoor surface to the middle of the thermal insulation.
        period_of_variations : float
            assumed period of variations in seconds for the 'EN ISO 13786:2017 Annex C.2.4 Effective thickness method'.
        heatsys_skiprows : array
            row indices to skip when reading AmBIENCe heating system data.
        """
        self.data = self.preprocess_data(
            building_stock_properties_path,
            building_stock_heatsys_path,
            heatsys_skiprows,
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
        self.fenestration = pd.read_csv(fenestration_path).set_index(
            [
                "REFERENCE BUILDING WINDOW GLAZING TYPE",
                "REFERENCE BUILDING WINDOW COATED",
            ]
        )
        self.ventilation = pd.read_csv(ventilation_path)

    def preprocess_data(
        self,
        building_stock_properties_path,
        building_stock_heatsys_path,
        heatsys_skiprows,
    ):
        """
        Preprocess AmBIENCe data to make it more manageable.

        Parameters
        ----------
        building_stock_properties_path : str
            path to the 'AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx' raw data file.
        building_stock_heatsys_path : str
            path to the 'AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx' raw data file.
        heatsys_skiprows : array
            row indices to skip when reading AmBIENCe heating system data.

        Returns
        -------
        data
            a DataFrame containing the combined and extended AmBIENCe data.
        """
        data = pd.merge(  # Merge the data together to make it easier to deal with.
            pd.read_excel(building_stock_properties_path),
            pd.read_excel(
                building_stock_heatsys_path, skiprows=heatsys_skiprows
            ),  # Skip first row of header, later headers will be omitted through inner join.
            left_on="REFERENCE BUILDING CODE",
            right_on="Building typology",
        )
        # Normalize heating system prevalency to avoid distorting the statistics just to be sure (there was a bug in the raw data).
        cols = [f"HEATING SYSTEM {i} PREVALENCY ON BUILDING STOCK" for i in (1, 2, 3)]
        tot = data[cols].sum(axis=1)
        for c in cols:
            data[c] = data[c] / tot
        # Create and add `building_period` to avoid dealing with it manually all the time.
        data["building_period"] = data[
            [
                "REFERENCE BUILDING CONSTRUCTION YEAR LOW",
                "REFERENCE BUILDING CONSTRUCTION YEAR HIGH",
            ]
        ].apply(lambda row: "-".join(row.values.astype(str)), axis=1)
        # Calculate structure weights for each row
        col = "BUILDING STOCK SEGMENT USEFUL FLOOR AREA (m2)"
        cols = [
            "REFERENCE BUILDING USE CODE",
            "building_period",
            "REFERENCE BUILDING COUNTRY CODE",
        ]
        data = data.set_index(cols)
        agg_data = data.groupby(cols).agg(
            total_area_over_material_combinations_m2=(col, sum)
        )
        data = data.join(agg_data)
        data["material_combination_weight"] = (
            data[col] / data["total_area_over_material_combinations_m2"]
        )
        return data.reset_index().set_index("REFERENCE BUILDING CODE")

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
    ):
        """
        Calculate the effective thermal mass according to 'EN ISO 13786:2017 Annex C.2.4 effective thickness method'.

        Note that internal structures assume no insulation.

        Parameters
        ----------
        r : DataFrame
            row of the raw AmBIENCe data used for the calculations.
        st : str
            the ABM structure type currently being processed.

        Returns
        -------
        effective_thermal_mass_J_m2K
        """
        pretext = " ".join(
            ["REFERENCE BUILDING", self.structure_types.loc[st, "mapping"]]
        )
        shc = (
            r[" ".join([pretext, "MATERIAL THICKNESS (m)"])]
            * r[" ".join([pretext, "MATERIAL DENSITY (kg/m3)"])]
            * r[" ".join([pretext, "MATERIAL SPECIFIC HEAT CAPACITY (J/kg/K)"])]
            + (
                not self.structure_types.loc[st, "is_internal"]
            )  # Internal structures assume no insulation.
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

    def calculate_U_values(self, r, st):
        """
        Calculate U-values for structure types.

        Note that internal structures assume no insulation.
        Ground-coupled heat losses based on 'Kissock. K., Simplified Model for Ground Heat Transfer from Slab-on-Grade Buildings, (c) 2013 ASHRAE'

        Parameters
        ----------
        r : DataFrame
            row of the raw AmBIENCe data used for the calculations.
        st : str
            the ABM structure type currently being processed.

        Returns
        -------
        U_values_W_m2K
            a tuple containing the exterior, ground, interior, and total U-values of the structure.
        """
        pretext = " ".join(
            ["REFERENCE BUILDING", self.structure_types.loc[st, "mapping"]]
        )
        material_resistance = (
            r[" ".join([pretext, "MATERIAL THICKNESS (m)"])]
            / r[" ".join([pretext, "MATERIAL THERMAL CONDUCTIVITY (W/m/K)"])]
        )
        insulation_resistance = (
            r[" ".join([pretext, "INSULATION MATERIAL THICKNESS (m)"])]
            / r[" ".join([pretext, "INSULATION MATERIAL THERMAL CONDUCTIVITY (W/m/K)"])]
        )
        # Internal structures assume no insulation.
        if self.structure_types.loc[st, "is_internal"]:
            intR = (
                self.interior_node_depth * 0.5 * material_resistance
                + self.structure_types.loc[st, "interior_resistance_m2K_W"]
            )
            extR = (
                2 - self.interior_node_depth
            ) * 0.5 * material_resistance + self.structure_types.loc[
                st, "exterior_resistance_m2K_W"
            ]
            return (1.0 / extR, 0.0, 1.0 / intR, 1.0 / (extR + intR))
        elif st == "base_floor":  # Base floor connects to the ground.
            intR = (
                self.interior_node_depth
                * (material_resistance + 0.5 * insulation_resistance)
                + self.structure_types.loc[st, "interior_resistance_m2K_W"]
            )
            flrR = (
                material_resistance
                + insulation_resistance
                + self.structure_types.loc[st, "interior_resistance_m2K_W"]
            )
            grnR = 1.0 / (0.114 / (0.7044 + flrR) + 0.8768 / (2.818 + flrR))
            grnR -= intR
            return (0.0, 1.0 / grnR, 1.0 / intR, 1.0 / (intR + grnR))
        else:  # Other structures connect to the ambient air.
            intR = (
                self.interior_node_depth
                * (material_resistance + 0.5 * insulation_resistance)
                + self.structure_types.loc[st, "interior_resistance_m2K_W"]
            )
            extR = (
                material_resistance
                + insulation_resistance
                + self.structure_types.loc[st, "interior_resistance_m2K_W"]
                + self.structure_types.loc[st, "exterior_resistance_m2K_W"]
                - intR
            )
            return (1.0 / extR, 0.0, 1.0 / intR, 1.0 / (extR + intR))

    def calculate_structure_statistics(self):
        """
        Process structural statistics from data for ArchetypeBuildingModel.jl.

        Returns
        -------
        structural_statistics
            a DataFrame for structure_statistics.csv export.
        """
        return (
            pd.DataFrame(
                [
                    [
                        r["REFERENCE BUILDING USE CODE"],
                        r["building_period"],
                        r["REFERENCE BUILDING COUNTRY CODE"],
                        st,
                        r["material_combination_weight"]
                        * r[
                            " ".join(
                                [
                                    "REFERENCE BUILDING",
                                    self.structure_types.loc[st, "mapping"],
                                    "U-VALUE (W/m2/K)",
                                ]
                            )
                        ],
                        r["material_combination_weight"]
                        * self.calculate_weighted_effective_thermal_mass(
                            r,
                            st,
                        ),
                        r["material_combination_weight"]
                        * self.structure_types.loc[st, "linear_thermal_bridge_W_mK"],
                    ]
                    + [
                        r["material_combination_weight"] * x
                        for x in self.calculate_U_values(r, st)
                    ]
                    for ((i, r), st) in product(
                        self.data.iterrows(), self.structure_types.index
                    )
                ],
                columns=[
                    "building_type",
                    "building_period",
                    "location_id",
                    "structure_type",
                    "design_U_value_m2K",
                    "effective_thermal_mass_J_m2K",
                    "linear_thermal_bridges_W_mK",
                    "external_U_value_to_ambient_air_W_m2K",
                    "external_U_value_to_ground_W_m2K",
                    "internal_U_value_to_structure_W_m2K",
                    "total_U_value_W_m2K",
                ],
            )
            .groupby(
                ["building_type", "building_period", "location_id", "structure_type"]
            )
            .agg(
                {
                    "design_U_value_m2K": "sum",
                    "effective_thermal_mass_J_m2K": "sum",
                    "linear_thermal_bridges_W_mK": "sum",
                    "external_U_value_to_ambient_air_W_m2K": "sum",
                    "external_U_value_to_ground_W_m2K": "sum",
                    "internal_U_value_to_structure_W_m2K": "sum",
                    "total_U_value_W_m2K": "sum",
                }
            )
        )

    def calculate_ventilation_and_fenestration_statistics(self):
        """
        Process ventilation and fenestration statistics for ArchetypeBuildingModel.jl.

        Note that AmBIENCe data contains no information related to ventilation
        or infiltration whatsoever, even though they tend to be very significant
        when it comes to heat losses from buildings.

        Returns
        -------
        ventilation_and_fenestration_statistics
            a DataFrame for `ventilation_and_fenestration_statistics.csv` export.
        """
        return (
            pd.DataFrame(
                [
                    [
                        r["REFERENCE BUILDING USE CODE"],
                        r["building_period"],
                        r["REFERENCE BUILDING COUNTRY CODE"],
                        r["material_combination_weight"]
                        * self.ventilation["HRU_efficiency"][0],
                        r["material_combination_weight"]
                        * self.ventilation["infiltration_rate_1_h"][0],
                        r["material_combination_weight"]
                        * self.fenestration.loc[
                            (
                                r["REFERENCE BUILDING WINDOW GLAZING TYPE"],
                                r["REFERENCE BUILDING WINDOW COATED"],
                            ),
                            "normal_solar_energy_transmittance",
                        ]
                        * (
                            1
                            - self.fenestration.loc[
                                (
                                    r["REFERENCE BUILDING WINDOW GLAZING TYPE"],
                                    r["REFERENCE BUILDING WINDOW COATED"],
                                ),
                                "frame_area_fraction",
                            ]
                        ),
                        r["material_combination_weight"]
                        * self.ventilation["ventilation_rate_1_h"][0],
                        r["material_combination_weight"]
                        * r["REFERENCE BUILDING WINDOW U-VALUE (W/m2/K)"],
                    ]
                    for (i, r) in self.data.iterrows()
                ],
                columns=[
                    "building_type",
                    "building_period",
                    "location_id",
                    "HRU_efficiency",
                    "infiltration_rate_1_h",
                    "total_normal_solar_energy_transmittance",
                    "ventilation_rate_1_h",
                    "window_U_value_W_m2K",
                ],
            )
            .groupby(["building_type", "building_period", "location_id"])
            .agg(
                {
                    "HRU_efficiency": "sum",
                    "infiltration_rate_1_h": "sum",
                    "total_normal_solar_energy_transmittance": "sum",
                    "ventilation_rate_1_h": "sum",
                    "window_U_value_W_m2K": "sum",
                }
            )
        )


class ABMDataset:
    """An object class for containing and exporting ArchetypeBuildingModel.jl compatible data."""

    def __init__(self, ambdata):
        """
        Process the AmBIENCe project raw data for ArchetypeBuildingModel.jl.

        Parameters
        ----------
        ambdata : AmBIENCeDataset
            the pre-processed AmBIENCe dataset used as the basis for the ABM.jl data.
        """
        self.building_period = ambdata.building_periods()
        self.building_stock = ambdata.building_stocks
        self.structure_type = ambdata.structure_types.drop(columns=["mapping"])
        self.building_stock_statistics = ambdata.calculate_building_stock_statistics()
        self.structure_statistics = ambdata.calculate_structure_statistics()
        self.ventilation_and_fenestration_statistics = (
            ambdata.calculate_ventilation_and_fenestration_statistics()
        )

    def export_csvs(self, folderpath="data/"):
        """
        Export the ABMDataset contents as .csv files.

        Parameters
        ----------
        folderpath : str
            the folder path where to export the contents.

        Returns
        -------
        a bunch of .csv files as output, but the function returns nothing.
        """
        self.building_period.to_csv(folderpath + "building_period.csv")
        self.building_stock.to_csv(folderpath + "building_stock.csv")
        self.structure_type.to_csv(folderpath + "structure_type.csv")
        self.building_stock_statistics.to_csv(
            folderpath + "building_stock_statistics.csv"
        )
        self.structure_statistics.to_csv(folderpath + "structure_statistics.csv")
        self.ventilation_and_fenestration_statistics.to_csv(
            folderpath + "ventilation_and_fenestration_statistics.csv"
        )

    def create_datapackage(self, folderpath="data/"):
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
        pkg.name = "ambience2abm"
        pkg.licenses = [
            {
                "name": "CC-BY-4.0",
                "path": "https://creativecommons.org/licenses/by/4.0/",
                "title": "Creative Commons Attribution 4.0",
            }
        ]
        pkg.profile = "data-package"
        pkg.title = "AmBIENCe2ABM"
        pkg.description = "A datapackage processed from AmBIENCe project EU27 building stock data for use with ArchetypeBuildingModel.jl."
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
            "mopo",
            "ABM.jl",
            "ArchetypeBuildingModel.jl",
        ]
        pkg.created = datetime.today().isoformat()
        return pkg
