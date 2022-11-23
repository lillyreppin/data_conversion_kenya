import pandas as pd
import numpy as np
import os
import random

class Scenarios:
    def __init__(self, path_to_extrema_input: str):
        self.path_to_extrema_input = path_to_extrema_input

        # read in csv files
        self.extrema_input_data = pd.read_csv(self.path_to_extrema_input)

    def scenario_generation(self):

        extrema_input = self.extrema_input_data.copy()
        
        # define variables for extrema
        a = extrema_input["cap_min_final"]
        b = extrema_input["cap_max_final"]
        c = extrema_input["fix_min_final"]
        d = extrema_input["fix_max_final"]

        # randomize capital and fixed costs within the min/max range
        for i in range(len(extrema_input)):
            y = random.uniform(a,b)
        
        for x in range(len(extrema_input)):
            z = random.uniform(c,d)
        
        # save randomized values in new column
        extrema_input["cap_random"] = y
        extrema_input["fix_random"] = z
        # print(extrema_input)
        # print(z.loc[extrema_input.index[104]])
        return extrema_input

PATH_EXTREMA_INPUT = "/Users/lilly/data_conversion_kenya/"
test = Scenarios(
    path_to_extrema_input=os.path.join(PATH_EXTREMA_INPUT, "final_cap_var_extrema.csv"))

final_frame = test.scenario_generation()