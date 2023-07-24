# process_ambience_data.py

# Classes and methods for processing the AmBIENCe datasets.

import pandas as pd


class AmBIENCeDataset:
    """An object class for containing and processing the raw AmBIENCe data."""

    def __init__(
        self,
        building_stock_properties_path="ambience_data/AmBIENCe_Deliverable-4.1_Database-of-greybox-model-parameter-values.xlsx",
        building_stock_heatsys_path="ambience_data/AmBIENCe-WP4-T4.2-Buildings_Energy_systems_Database_EU271.xlsx",
        structure_types_path="assumptions/structure_types.csv",
        building_stock_path="assumptions/building_stock.csv",
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
        """
        self.statistics_df = pd.read_excel(building_stock_properties_path)
        self.heatsys_df = pd.read_excel(
            building_stock_heatsys_path, skiprows=[0, 1734, 1735]
        )  # Need to skip unnecessary header rows at the start and in the middle...

    def building_periods(self):
        """
        Processes the unique building periods from the data.

        Returns
        -------
        building_periods_df
            a DataFrame for building period .csv export.
        """
        bps = pd.unique(
            list(
                zip(
                    *[
                        self.statistics_df[col]
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


class ABMDataset:
    """An object class for containing and exporting ArchetypeBuildingModel.jl compatible data."""

    def __init__(self, ambience_data):
        """
        Process the AmBIENCe project raw data for ArchetypeBuildingModel.jl.

        Parameters
        ----------

        """
