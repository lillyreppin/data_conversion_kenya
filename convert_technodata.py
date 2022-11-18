import pandas as pd
import numpy as np
import os


# Technology keys in base model (left, key) and US database (right, value)
TECHNO_MAPPING_DICT = {
    "Biomass Power Plant": "Biopower - Dedicated",
    "CSP with Storage": "CSP - Class",  # class 2-7
    "CSP without Storage": "CSP - Class",  # class 2-7
    "Coal Power Plant": "Coal",
    "Gas Power Plant (CCGT)": "NG F-Frame CC",
    "Gas Power Plant (SCGT)": "NG F-Frame CT",
    "Geothermal Power Plant": "Geothermal",
    "Large Hydropower Plant (Dam) (>100MW)": "Pumped Storage Hydropower - National Class",  # upwards
    # "Light Fuel Oil Power Plant	": "	-	",
    # "Light Fuel Oil Standalone Generator (1kW)	": "	-	",
    "Medium Hydropower Plant (10-100MW)": "Hydropower - NPD",
    "Nuclear Power Plant": "Nuclear",
    "Offshore Wind": "Offshore Wind - Class",
    # "Oil Fired Gas Turbine (SCGT)	": "	-	",
    "Onshore Wind": "Land-Based Wind - Class",
    "Small Hydropower Plant (<10MW)": "Hydropower - NPD",
    "Solar PV (Distributed with Storage)": "PV\+Storage - Class",  # class 2-7
    "Solar PV (Utility)": "Utility PV - Class",  # class 2-7
}


# values: [min, max]
TECHNO_RANGE_DICT = {
    # "Biopower - Dedicated": ["const", 0.1],
    "CSP - Class": [2, 7],
    # "Coal": "all",
    # "NG F-Frame CC": "",
    # "NG F-Frame CT": ["const", 0.1],
    # "Geothermal": "all",
    "Pumped Storage Hydropower - National Class": [8, 100],
    # "Nuclear": "all",
    "Hydropower - NPD": [5, 7],
    "Offshore Wind - Class": [2, 4],
    "Land-Based Wind - Class": [8, 10],
    "PV\+Storage - Class": [2, 7],
    "Utility PV - Class": [2, 7],
}


LIFETIME_METRIC = {
    "Biopower - Dedicated": 30,
    "CSP - Class": 30,
    "Coal": 35,
    "NG F-Frame CC": 25,
    "NG F-Frame CT": 25,
    "Geothermal": 25,
    "Pumped Storage Hydropower - National Class": 50,
    "Hydropower - NPD": 50,
    "Nuclear": 50,
    "Offshore Wind - Class": 25,
    "Land-Based Wind - Class": 25,
    "PV\+Storage - Class": 24,
    "Utility PV - Class": 24,
}

YEARS_OF_INTEREST = [2020, 2025, 2030, 2040, 2050]


class TechnoData:
    def __init__(self, path_to_base_input: str, path_to_us_database: str):
        self.path_to_base_input = path_to_base_input
        self.path_to_us_database = path_to_us_database

        # read in csv files
        self.base_input_data = pd.read_csv(self.path_to_base_input)
        self.us_data = pd.read_csv(self.path_to_us_database)

        # create dataframe to allow conversion and scaling
        self.scaling_df = pd.DataFrame(
            columns=[
                "technology",
                "year",
                "fix_mean_base",
                "fix_mean_US",
                "fix_min",
                "fix_max",
                "cap_mean_base",
                "cap_mean_US",
                "cap_min",
                "cap_max",
            ]
        )

    def extract_mean_from_base_model(self):
        """
        Fills data with entries from base model.
        """

        # create dataframe to allow conversion and scaling
        truncated_base_data = pd.DataFrame(
            columns=["ProcessName", "Time", "cap_par", "fix_par"]
        )

        # create dummy frame
        dummy = self.base_input_data.copy()

        # delete unit row
        dummy = dummy.drop(0)

        # convert columns to floats and integers
        # integers first
        dummy["Time"] = dummy["Time"].astype(int)

        # floats second
        dummy[["cap_par", "fix_par"]] = dummy[["cap_par", "fix_par"]].astype(float)

        # loop over technologies
        for tech in TECHNO_MAPPING_DICT.keys():

            # get relevant rows
            df_base = dummy.loc[
                (dummy["ProcessName"] == tech) & (dummy["Time"].isin(YEARS_OF_INTEREST))
            ]

            # get relevant columns
            df_base_relevant = df_base[["ProcessName", "Time", "cap_par", "fix_par"]]

            truncated_base_data = truncated_base_data.append(df_base_relevant)

        truncated_base_data = truncated_base_data.rename(
            columns={
                "ProcessName": "technology",
                "Time": "year",
                "cap_par": "cap_mean_base",
                "fix_cap": "fix_mean_base",
            }
        )

        return truncated_base_data

    def extract_extrema_from_US_database(self, scenario: str = "Moderate"):
        """
        Fills data with entries from base model.
        """

        US_data_fix = pd.DataFrame(
            columns= ["year","fix_mean_US", "fix_min_US", "fix_max_US", "technology"]
        )

        # loop over technologies
        for code, tech in TECHNO_MAPPING_DICT.items():
            print(tech)

            # get relevant rows
            df_US = self.us_data.loc[
                (self.us_data["display_name"].str.contains(tech).fillna(False))
                & (self.us_data["core_metric_variable"].isin(YEARS_OF_INTEREST))
                & (self.us_data["scenario"] == scenario)
                & (self.us_data["core_metric_case"] == "R&D")
                & (self.us_data["core_metric_parameter"] == "Fixed O&M")
            ]
            # decide for lifetime
            # lifetimes given by US database
            lifetimes_for_tech = np.sort(
                np.asarray(df_US.crpyears.unique()).astype(int)
            )

            # get closest to value given base model
            lifetime_chosen = lifetimes_for_tech[
                np.argmin(np.abs(lifetimes_for_tech - LIFETIME_METRIC.get(tech)))
            ]

            # get data with the respective lifetime
            df_US = df_US.loc[df_US["crpyears"].astype(int) == lifetime_chosen]

            # now get ranges for technologies with multiple classes
            if tech in TECHNO_RANGE_DICT.keys():

                # get min and max categories
                min_cat, max_cat = (
                    TECHNO_RANGE_DICT.get(tech)[0],
                    TECHNO_RANGE_DICT.get(tech)[1],
                )

                # create list of potential categories as strings
                allowed_cat_strings = [
                    tech + f" {cat}" for cat in np.arange(min_cat, max_cat + 1)
                ]

                # modify dataframe in a way that only those categories are left
                df_US = df_US.loc[df_US.display_name.isin(allowed_cat_strings)]

            # deal with CCS in natural gas plants separately
            if "NG F-Frame CC" in tech:
                df_US = df_US.loc[df_US["display_name"] == tech]

            # having done all the filtering and categorisation, we can move on to create our dataframe
            df_US_grouped = (
                df_US.groupby("core_metric_variable")
                .agg({"value": ["mean", "min", "max"]})
                .pipe(lambda x: x.set_axis(x.columns.map("_".join), axis=1))
            )
            df_US_grouped["technology"] = TECHNO_MAPPING_DICT.get(code)
            df_US_grouped["year"] = df_US_grouped.index
            df_US_grouped = df_US_grouped.rename(
                columns={
                    "value_mean": "fix_mean_US",
                    "value_min": "fix_min_US",
                    "value_max": "fix_max_US",
                }
            ).reset_index().drop(columns = "core_metric_variable")

            # now append to big dataframe
            US_data_fix = US_data_fix.append(df_US_grouped)

        return US_data_fix


#  "technology",
# "year",
# "cap_mean_base",
# "fix_mean_base",


PATH_BASE_INPUT = "/Users/lilly/MUSE-starter-kits-converter-main/data/processed/kenya_scenarios/Kenya/base/technodata/power"
PATH_US_DATABASE = "/Users/lilly/norm"
test = TechnoData(
    path_to_base_input=os.path.join(PATH_BASE_INPUT, "Technodata.csv"),
    path_to_us_database=os.path.join(PATH_US_DATABASE, "ATB2022.csv"),
)

# base_data_sorted = test.extract_mean_from_base_model()
us_data_sorted = test.extract_extrema_from_US_database()
breakpoint()
