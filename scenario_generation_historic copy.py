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

    def scenario_generation(self):

        extrema_input = self.extrema_input_data.copy()

        # delete first empty column
        extrema_input = extrema_input.drop(["Unnamed: 0"], axis = 1)
        
        # define variables for extrema
        a = extrema_input["cap_min_final"]
        b = extrema_input["cap_max_final"]
        c = extrema_input["fix_min_final"]
        d = extrema_input["fix_max_final"]

        # randomize capital costs within the min/max range
        for i in range(len(extrema_input)):
            y = random.uniform(a,b)
        # randomize fixed costs within the min/max range
        for x in range(len(extrema_input)):
            z = random.uniform(c,d)
        
        # save randomized values in new column
        extrema_input["cap_random"] = y
        extrema_input["fix_random"] = z
        extrema_input_final = extrema_input
        print(extrema_input_final)
        # print(z.loc[extrema_input.index[104]])

        base_input = self.base_input_data.copy()

        # give path for scenarios
        scenario_path = r'/Users/lilly/muse_kenya/run/Scenarios/'
        source_path = r'/Users/lilly/muse_kenya/run/Kenya/base'

        # for-loop scenario generation
        # copy files
        for num in range(0, 3):
           test = scenario_path + "Scenario_" + str(num)
           #os.mkdir(scenario_path + "Scenario_" + str(num))
           os.mkdir(test)
           os.path.join(scenario_path,os.path.basename(source_path))
           shutil.copytree(source_path, test, dirs_exist_ok=True)

           # in technodata file: randomize cap_par according to cap_random
           path_techno_data = "/Users/lilly/muse_kenya/run/Scenarios/" + "Scenario_" + str(num) + "/technodata/power/technodata.csv"
           technodata = pd.read_csv(path_techno_data)
           technodata = technodata.copy()
           technodata["cap_random"] = extrema_input["cap_random"]
           
           # change column "cap_par" in technodata.csv -> on doesn't exist for base_input!

           #base_input["cap_par"] = np.where(extrema_input_final["cap_random"] != , on = ["technology", "year"])
        
        return self


PATH_EXTREMA_INPUT = "/Users/lilly/data_conversion_kenya/"
PATH_BASE_INPUT = "/Users/lilly/muse_kenya/run/Kenya/base/technodata/power"
test = Scenarios(
    path_to_extrema_input=os.path.join(PATH_EXTREMA_INPUT, "final_cap_var_extrema.csv"),
    path_to_base_input=os.path.join(PATH_BASE_INPUT, "Technodata.csv"))

final_frame = test.scenario_generation()