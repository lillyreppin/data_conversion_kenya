import pandas as pd
import numpy as np
import os


# Technology keys in base model (left, key) and US database (right, value)
TECHNO_MAPPING_DICT = {
    "Biomass Power Plant": "Biopower",
    "CSP with Storage": "CSP",
    "CSP without Storage": "CSP",
    "Coal Power Plant": "Coal",
    "Gas Power Plant (CCGT)": "Natural Gas",
    "Gas Power Plant (SCGT)": "Natural Gas",
    "Geothermal Power Plant": "Geothermal",
    "Large Hydropower Plant (Dam) (>100MW)": "Hydropower",
    # "Light Fuel Oil Power Plant	": "	-	",
    # "Light Fuel Oil Standalone Generator (1kW)	": "	-	",
    "Medium Hydropower Plant (10-100MW)": "Hydropower",
    "Nuclear Power Plant": "Nuclear",
    "Offshore Wind": "Offshore wind",
    # "Oil Fired Gas Turbine (SCGT)	": "	-	",
    "Onshore Wind": "Land-based wind",
    "Small Hydropower Plant (<10MW)": "Hydropower",
    "Solar PV (Distributed with Storage)": "Utility-Scale PV-Plus-Battery",
    "Solar PV (Utility)": "Utility PV",
}

LIFETIME_METRIC = {
    "Biopower": 30,
    "CSP": 30,
    "Coal": 35,
    "Natural Gas": 25,
    "Geothermal": 25,
    "Hydropower":50,
    "Nuclear": 50,
    "Offshore wind": 25,
    "Land-based wind": 25,
    "Utility-Scale PV-Plus-Battery": 24,
    "Utility PV": 24,
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

    def extract_extrema_from_US_database(self):
        """
        Fills data with entries from base model.
        """

        # create dataframe to allow conversion and scaling
        # truncated_US_data_cap = pd.DataFrame(
        #     columns=["core_metric_variable", "technology_alias", "value"]
        # )

        truncated_US_data_fix = pd.DataFrame(
            columns=["core_metric_variable", "technology_alias", "value"]
        )

        # loop over technologies
        for tech in TECHNO_MAPPING_DICT.values():
            print(tech)
            # get relevant rows
            df_US = self.us_data.loc[
                (self.us_data["technology_alias"] == tech)
                & (
                    self.us_data["core_metric_variable"].isin(YEARS_OF_INTEREST))
                    & (self.us_data["scenario"] == "Moderate")
                    & (self.us_data["core_metric_case"] == "R&D")
                
            ]

            df_US_fix = df_US.loc[
                (self.us_data["core_metric_parameter"] == "Fixed O&M")
            ]
            if "Natural" in tech:
                breakpoint()

            # decide for lifetime
            # lifetimes given by US database
            lifetimes_for_tech = np.sort(np.asarray(df_US_fix.crpyears.unique()).astype(int))
            
            # get closest to value given base model
            lifetime_chosen = lifetimes_for_tech[np.argmin(np.abs(lifetimes_for_tech-LIFETIME_METRIC.get(tech)))]
            
            # get data with the respective lifetime
            df_US_fix = df_US_fix.loc[df_US_fix["crpyears"].astype(int)==lifetime_chosen]

        

        #     # get relevant columns
        #     df_US_relevant = df_US[["technology_alias", "core_metric_variable", "", ""]]

        #     truncated_US_data = self.truncated_base_data.append(df_US_relevant)

        # truncated_US_data = self.truncated_US_data.rename(
        #     columns={
        #         "technology_alias": "technology",
        #         "core_metric_variable": "year",
        #     }
        # )

        return truncated_base_data


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
# test.scaling()
