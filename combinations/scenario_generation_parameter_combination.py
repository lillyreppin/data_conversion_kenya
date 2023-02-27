import pandas as pd
import numpy as np
import os
import random
import shutil


class Scenarios:
    def __init__(self, path_to_cost_input: str, path_to_base_input: str, path_to_lifetime_input: str, path_to_capacity_input: str):
        self.path_to_base_input = path_to_base_input
        self.path_to_capacity_input = path_to_capacity_input
        self.path_to_cost_input = path_to_cost_input
        self.path_to_lifetime_input = path_to_lifetime_input
        # read in csv files
        self.base_input_data = pd.read_csv(self.path_to_base_input)
        self.capacity_input_data = pd.read_csv(self.path_to_capacity_input)
        self.cost_input_data = pd.read_csv(self.path_to_cost_input)
        self.lifetime_input_data = pd.read_csv(self.path_to_lifetime_input)

    def scenario_generation(self, n_scenarios: int = []):
        """
        Generate a specific number of scenarios for selected US_scenario, randomise the values for capital and fixed costs as well as lifetime.
        """

        capacity_input = self.capacity_input_data.copy()
        cost_input = self.cost_input_data.copy()
        lifetime_input = self.lifetime_input_data.copy()

        # delete first empty column and rename cost_input based on technodata column names
        cost_input = cost_input.drop(["Unnamed: 0"], axis=1).rename(
            columns={"technology": "ProcessName", "year": "Time"}
        )

        # define variables for cost extrema
        cap_min_final = cost_input["cap_min_final"]
        cap_max_final = cost_input["cap_max_final"]
        fix_min_final = cost_input["fix_min_final"]
        fix_max_final = cost_input["fix_max_final"]
        lifetime_min = lifetime_input["TechnicalLife"]
        lifetime_max = lifetime_input["TechnicalLife_mod"]

        # give path for scenarios
        scenario_path = r"/../../.." # add the path
        source_path = r"/../../.." # add the path

        scenarios = ["..."] # add the requested US_scenario

        for US_scenario in scenarios:

            # for-loop scenario generation
            for num in range(0, n_scenarios):
                scenario_path_final = scenario_path + str(num)
                if not os.path.exists(scenario_path_final):
                    os.mkdir(scenario_path_final)

                os.path.join(scenario_path, os.path.basename(source_path))
                shutil.copytree(source_path, scenario_path_final, dirs_exist_ok=True)

                # randomise capital costs within the min/max range
                cost_input["cap_random"] = random.uniform(
                    cap_min_final, cap_max_final
                )
                # randomise fixed costs within the min/max range
                cost_input["fix_random"] = random.uniform(
                    fix_min_final, fix_max_final
                )

                # randomise lifetime
                lifetime_input["TechnicalLife_random"] = random.uniform(
                    lifetime_min, lifetime_max
                )

                # in techno data file: randomise "cap_par" according to "cap_random"
                path_techno_data = (
                    scenario_path
                    + str(num)
                    + "/technodata/power/Technodata.csv"
                )
                technodata = pd.read_csv(path_techno_data)
                cost_input = cost_input.astype({"Time": str})
                cost_input_scenario_chosen = cost_input.loc[
                    cost_input.US_scenario == US_scenario
                ]

                # change columns "cap_par" and "fix_par" in Technodata.csv
                technodata_final = pd.merge(
                    left=technodata,
                    right=cost_input_scenario_chosen[
                        [
                            "ProcessName",
                            "Time",
                            "cap_random",
                            "fix_random",
                            "US_scenario",
                        ]
                    ],
                    how="left",
                    left_on=["ProcessName", "Time"],
                    right_on=["ProcessName", "Time"],
                )

                technodata_final["cap_par"] = np.where(
                    technodata_final["cap_random"] > 0,
                    technodata_final["cap_random"],
                    technodata_final["cap_par"],
                )
                technodata_final["fix_par"] = np.where(
                    technodata_final["fix_random"] > 0,
                    technodata_final["fix_random"],
                    technodata_final["fix_par"],
                )
                technodata_final = technodata_final.drop(
                    columns=["US_scenario", "cap_random", "fix_random"]
                )

                # in techno data file: randomise "TechnicalLife" according to "TechnicalLife_random"
                lifetime_input = lifetime_input.astype({"Time": str})
                technodata_final2 = pd.merge(
                    left=technodata_final,
                    right=lifetime_input[
                        ["ProcessName", "Time", "TechnicalLife_random"]
                    ],
                    how="left",
                    left_on=["ProcessName", "Time"],
                    right_on=["ProcessName", "Time"],
                )
                technodata_final2["TechnicalLife"] = np.where(
                    technodata_final2["TechnicalLife_random"] > 0,
                    technodata_final2["TechnicalLife_random"],
                    technodata_final2["TechnicalLife"],
                )
                technodata_final2 = technodata_final2.drop(
                    columns=["TechnicalLife_random"]
                )    
                
                # in techno data file: adapt capacity according to MaxCapacityAddition_mod and MaxCapacityGrowth_mod
                capacity_input = capacity_input.astype({"Time": str})
                technodata_final3 = pd.merge(
                    left=technodata_final2,
                    right=capacity_input[
                        ["ProcessName", "Time", "MaxCapacityAddition_mod", "MaxCapacityGrowth_mod"]
                    ],
                    how="left",
                    left_on=["ProcessName", "Time"],
                    right_on=["ProcessName", "Time"],
                )
                technodata_final3["MaxCapacityAddition"] = technodata_final3["MaxCapacityAddition_mod"]
                technodata_final3["MaxCapacityGrowth"] = technodata_final3["MaxCapacityGrowth_mod"]

                technodata_final3 = technodata_final3.drop(
                    columns=["MaxCapacityAddition_mod", "MaxCapacityGrowth_mod"]
                )                           

                os.remove(path_techno_data)
                technodata_final3.to_csv(path_techno_data)

        return self

PATH_BASE_INPUT = "/../../.." # add the path
PATH_CAPACITY_INPUT = "/../../.." # add the path
PATH_COST_INPUT = "/../../.." # add the path
PATH_LIFETIME_INPUT = "/../../.." # add the path
scenario_input = Scenarios(
    path_to_base_input=os.path.join(PATH_BASE_INPUT, "..."), # add the file
    path_to_capacity_input=os.path.join(PATH_CAPACITY_INPUT, "..."), # add the file
    path_to_cost_input=os.path.join(PATH_COST_INPUT, "..."), # add the file
    path_to_lifetime_input=os.path.join(PATH_LIFETIME_INPUT, "..."), # add the file
)

final_frame = scenario_input.scenario_generation()
