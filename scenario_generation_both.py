import pandas as pd
import numpy as np
import os
import random
import shutil


class Scenarios:
    def __init__(self, path_to_extrema_input: str, path_to_base_input: str):
        self.path_to_extrema_input = path_to_extrema_input
        self.path_to_base_input = path_to_base_input
        # read in csv files
        self.extrema_input_data = pd.read_csv(self.path_to_extrema_input)
        self.base_input_data = pd.read_csv(self.path_to_base_input)

    def scenario_generation(self, n_scenarios: int = 10):
        """
        Generate a specific number of scenarios for each US_scenario and randomize the values for capital and fixed costs.
        """

        extrema_input = self.extrema_input_data.copy()

        # delete first empty column
        # rename extrema_input based on technodata column names
        extrema_input = extrema_input.drop(["Unnamed: 0"], axis=1).rename(
            columns={"technology": "ProcessName", "year": "Time"}
        )

        # define variables for extrema
        cap_min_final = extrema_input["cap_min_final"]
        cap_max_final = extrema_input["cap_max_final"]
        fix_min_final = extrema_input["fix_min_final"]
        fix_max_final = extrema_input["fix_max_final"]

        base_input = self.base_input_data.copy()

        # give path for scenarios
        scenario_path = r"/Users/lilly/muse_kenya/run/scenarios_capital_fix/"
        source_path = r"/Users/lilly/muse_kenya/run/Kenya/base"

        scenarios = extrema_input.US_scenario.unique().tolist()

        for US_scenario in scenarios:

            # for-loop scenario generation
            for num in range(0, n_scenarios):
                scenario_path_final = (
                    scenario_path + f"{US_scenario}_" + str(num)
                )
                # os.mkdir(scenario_path + "Scenario_" + str(num))
                if not os.path.exists(scenario_path_final):
                    os.mkdir(scenario_path_final)

                os.path.join(scenario_path, os.path.basename(source_path))
                shutil.copytree(source_path, scenario_path_final, dirs_exist_ok=True)

                # randomize capital costs within the min/max range
                extrema_input["cap_random"] = random.uniform(
                    cap_min_final, cap_max_final
                )
                # randomize fixed costs within the min/max range
                extrema_input["fix_random"] = random.uniform(
                    fix_min_final, fix_max_final
                )

                # in technodata file: randomize cap_par according to cap_random
                path_techno_data = (
                    "/Users/lilly/muse_kenya/run/scenarios_capital_fix/"
                    + f"{US_scenario}_"
                    + str(num)
                    + "/technodata/power/Technodata.csv"
                )
                technodata = pd.read_csv(path_techno_data)
                extrema_input = extrema_input.astype({"Time": str})
                extrema_input_scenario_chosen = extrema_input.loc[
                    extrema_input.US_scenario == US_scenario
                ]

                # change columns "cap_par" and "fix_par" in technodata.csv
                technodata_final = pd.merge(
                    left=technodata,
                    right=extrema_input_scenario_chosen[
                        ["ProcessName", "Time", "cap_random", "fix_random", "US_scenario"]
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
                    columns=["US_scenario", "fix_random", "cap_random"]
                )

                print(technodata_final)
                os.remove(path_techno_data)

                technodata_final.to_csv(path_techno_data)

        return self


PATH_EXTREMA_INPUT = "/Users/lilly/data_conversion_kenya/"
PATH_BASE_INPUT = "/Users/lilly/muse_kenya/run/Kenya/base/technodata/power"
scenario_input = Scenarios(
    path_to_extrema_input=os.path.join(PATH_EXTREMA_INPUT, "final_cap_var_extrema.csv"),
    path_to_base_input=os.path.join(PATH_BASE_INPUT, "Technodata.csv"),
)

final_frame = scenario_input.scenario_generation()
