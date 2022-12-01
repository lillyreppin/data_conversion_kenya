import pandas as pd
import numpy as np
import os

class Results:
    def __init__(
        self, path_to_capacity_input: str, path_to_emission_input: str):
        self.path_to_capacity_input = path_to_capacity_input
        self.path_to_emission_input = path_to_emission_input

        # read in csv files
        self.capacity_input = pd.read_csv(self.path_to_capacity_input)
        self.emission_input = pd.read_csv(self.path_to_emission_input)

PATH_MCACapacity = 
PATH_MCAMetric_Supply = 
Analyse = Results(path_to_capacity_input = os.path.join(PATH_MCACapacity, "MCACapacity.csv"), path_to_emission_input = os.path.join(PATH_MCAMetric_Supply, "MCAMetric_Supply.csv"))