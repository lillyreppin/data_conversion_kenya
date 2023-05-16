import pandas as pd
import numpy as np
import os
import random
import shutil


class Scenarios:
    def __init__(self, path_to_base_input: str, path_to_demand_2030: str, path_to_demand_2040: str, path_to_demand_2050: str, path_carbon_price_input: str, path_CCS_CommIn_input: str, path_CCS_CommOut_input: str, path_commodity_input: str, path_existing_capacity_input: str, path_technodata_input: str, path_timeslices_input: str):
        self.path_to_base_input = path_to_base_input
        self.path_to_demand_2030 = path_to_demand_2030
        self.path_to_demand_2040 = path_to_demand_2040
        self.path_to_demand_2050 = path_to_demand_2050
        self.path_carbon_price_input = path_carbon_price_input
        self.path_CCS_CommIn_input = path_CCS_CommIn_input
        self.path_CCS_CommOut_input = path_CCS_CommOut_input
        self.path_commodity_input = path_commodity_input
        self.path_existing_capacity_input = path_existing_capacity_input
        self.path_technodata_input = path_technodata_input
        self.path_timeslices_input = path_timeslices_input
        # read in csv files
        self.base_input_data = pd.read_csv(self.path_to_base_input)
        self.demand_2030_input = pd.read_csv(path_to_demand_2030)
        self.demand_2040_input = pd.read_csv(path_to_demand_2040)
        self.demand_2050_input = pd.read_csv(path_to_demand_2050)
        self.carbon_price_input = pd.read_csv(self.path_carbon_price_input)
        self.CCS_CommIn_input = pd.read_csv(path_CCS_CommIn_input)
        self.CCS_CommOut_input = pd.read_csv(path_CCS_CommOut_input)
        self.commodity_input = pd.read_csv(path_commodity_input)
        self.existing_capacity_input = pd.read_csv(path_existing_capacity_input)
        self.technodata_input = pd.read_csv(path_technodata_input)
        self.timeslices_input = pd.read_csv(path_timeslices_input)

    def scenario_generation(self, n_scenarios: int = 1):
        """
        Generate a specific number of scenarios and randomise the values for capital and fixed costs, lifetime, utilisation factor and efficiency to +/-30% as well as the capacity for fossil fuels to 0 from 2030 onwards.
        Additional options: randomise the energy demand, implement CCS technologies and a carbon price.
        """

        # technologys in the Kenya base model
        CCS_tech = [
            "Biomass Power Plant",
            "Coal Power Plant",
            "Gas Power Plant (SCGT)",
            "Gas Power Plant (CCGT)",
            "Light Fuel Oil Power Plant",
            "Light Fuel Oil Standalone Generator (1kW)",
            "Oil Fired Gas Turbine (SCGT)",
        ] 

        fossil = [
            "Coal Power Plant",
            "Gas Power Plant (SCGT)",
            "Gas Power Plant (CCGT)",
            "Light Fuel Oil Power Plant",
            "Light Fuel Oil Standalone Generator (1kW)",
            "Oil Fired Gas Turbine (SCGT)",
            "Nuclear Power Plant",
        ]

        renewables = [
            "Biomass Power Plant",
            "CSP with Storage",
            "CSP without Storage",
            "Geothermal Power Plant",
            "Large Hydropower Plant (Dam) (>100MW)",
            "Medium Hydropower Plant (10-100MW)",
            "Offshore Wind",
            "Onshore Wind",
            "Small Hydropower Plant (<10MW)",
            "Solar PV (Distributed with Storage)",
            "Solar PV (Utility)",
        ]

        # Read scenario combinations from file
        combinations_file = "/Users/lilly/muse_kenya/combinations.txt"

        with open(combinations_file, "r") as file:
            combinations = file.read().splitlines()

        # give path for scenarios
        #scenario_path = r"/Users/lilly/muse_kenya/run/costs_capacityThirty_utilisationFactor/"  # CHANGE PATH
        source_path = r"/Users/lilly/muse_kenya/run/Kenya/base/"

        # for-loop scenario generation path
        for i, combination in enumerate(combinations):
            # Create scenario directory
            words = combination.split(" - ")
            words_with_underscore = "_".join(words)
            scenario_path = f"/Users/lilly/muse_kenya/run/test/{words_with_underscore}/"  # CHANGE PATH
            os.makedirs(scenario_path, exist_ok=True)

            # for-loop scenario generation
            for num in range(0, n_scenarios):
                scenario_path_final = scenario_path + str(num)
                if not os.path.exists(scenario_path_final):
                    os.mkdir(scenario_path_final)

                os.path.join(scenario_path, os.path.basename(source_path))
                shutil.copytree(source_path, scenario_path_final, dirs_exist_ok=True)

                if "ccs" in scenario_path_final:
                    # modify CommIn.csv by adding "CCS " to CO2 emission technologies and muliply commodities by 1.32
                    path_CCS_CommIn = (
                        scenario_path_final
                        + "/technodata/power/CommIn.csv"
                    )

                    CommIn_base = self.CCS_CommIn_input.copy().drop(0)
                    CCS_CommIn = self.CCS_CommIn_input.copy()
                    unit_row = pd.read_csv(path_CCS_CommIn, nrows=1)

                    CCS_CommIn = CCS_CommIn.loc[CCS_CommIn.ProcessName.isin(CCS_tech)]
                    # add "CCS " to the beginning of the values in the "ProcessName" column
                    CCS_CommIn.loc[CCS_CommIn["ProcessName"].isin(CCS_tech), "ProcessName"] = 'CCS ' + CCS_CommIn.loc[CCS_CommIn["ProcessName"].isin(CCS_tech), "ProcessName"].astype(str)
                    CCS_CommIn[["biomass", "coal", "gas", "HFO", "LFO"]] = CCS_CommIn[["biomass", "coal", "gas", "HFO", "LFO"]].astype(float)
                    CCS_CommIn[["biomass", "coal", "gas", "HFO", "LFO"]] = CCS_CommIn[["biomass", "coal", "gas", "HFO", "LFO"]] * (1 + 0.32)

                    os.remove(path_CCS_CommIn)
                    CCS_CommIn_final = pd.concat([unit_row, CommIn_base, CCS_CommIn], ignore_index = True)
                    CCS_CommIn_final.to_csv(path_CCS_CommIn, index=False)

                    # modify CommOut.csv by adding "CCS " to CO2 emission technologies and muliply commodities as CommIn_new * emission_factor * 0.1 
                    # "biomass" is special case as carbon neutral technology
                    path_CCS_CommOut = (
                        scenario_path_final
                        + "/technodata/power/CommOut.csv"
                    )

                    CommOut_base = self.CCS_CommOut_input.copy().drop(0)
                    CCS_CommOut = self.CCS_CommOut_input.copy()
                    unit_row = pd.read_csv(path_CCS_CommOut, nrows=1)
                    commodities = self.commodity_input.copy()

                    CCS_CommOut = CCS_CommOut.loc[CCS_CommOut.ProcessName.isin(CCS_tech)]
                    # add "CCS " to the beginning of the values in the "ProcessName" column
                    CCS_CommOut.loc[CCS_CommOut["ProcessName"].isin(CCS_tech), "ProcessName"] = 'CCS ' + CCS_CommOut.loc[CCS_CommOut["ProcessName"].isin(CCS_tech), "ProcessName"].astype(str)
                    CCS_CommOut[["biomass", "coal", "gas", "HFO", "LFO"]] = CCS_CommOut[["biomass", "coal", "gas", "HFO", "LFO"]].astype(float)

                    #CCS_CommOut.loc[CCS_CommOut['ProcessName'] == 'CCS Biomass Power Plant', 'CO2f'] = (CCS_CommIn.loc[CCS_CommIn['ProcessName'] == 'CCS Biomass Power Plant', 'CO2f'].astype(float)*(1+0.32)) * commodities.loc[commodities['Commodity'] == 'Biomass', 'CommodityEmissionFactor_CO2'].astype(float) * (-1)
                    # Loop through each row in CCS_CommOut
                    for idx, row in CCS_CommOut.iterrows():
                        # Check if the 'ProcessName' column value is 'CCS Biomass Power Plant'
                        if row['ProcessName'] == 'CCS Biomass Power Plant':
                            CCS_CommOut.at[idx, 'CO2f'] = 3.771428571428572 * commodities.loc[commodities['Commodity'] == 'Biomass', 'CommodityEmissionFactor_CO2'].iloc[0] * (-1)
                        if row['ProcessName'] == 'CCS Coal Power Plant':
                            CCS_CommOut.at[idx, 'CO2f'] = 3.5675675675675675 * commodities.loc[commodities['Commodity'] == 'Coal', 'CommodityEmissionFactor_CO2'].iloc[0] * 0.1
                        if row['ProcessName'] == 'CCS Gas Power Plant (CCGT)':
                            CCS_CommOut.at[idx, 'CO2f'] = 2.7500000000000004 * commodities.loc[commodities['Commodity'] == 'Natural Gas', 'CommodityEmissionFactor_CO2'].iloc[0] * 0.1
                        if row['ProcessName'] == 'CCS Gas Power Plant (SCGT)':
                            CCS_CommOut.at[idx, 'CO2f'] = 4.4 * commodities.loc[commodities['Commodity'] == 'Natural Gas', 'CommodityEmissionFactor_CO2'].iloc[0] * 0.1
                        if row['ProcessName'] == 'CCS Light Fuel Oil Power Plant':
                            CCS_CommOut.at[idx, 'CO2f'] = 3.771428571428572 * commodities.loc[commodities['Commodity'] == 'Light Fuel Oil', 'CommodityEmissionFactor_CO2'].iloc[0] * 0.1
                        if row['ProcessName'] == 'CCS Light Fuel Oil Standalone Generator (1kW)':
                            CCS_CommOut.at[idx, 'CO2f'] = 8.25 * commodities.loc[commodities['Commodity'] == 'Light Fuel Oil', 'CommodityEmissionFactor_CO2'].iloc[0] * 0.1
                        if row['ProcessName'] == 'CCS Oil Fired Gas Turbine (SCGT)':
                            CCS_CommOut.at[idx, 'CO2f'] = 3.771428571428572 * commodities.loc[commodities['Commodity'] == 'Heavy Fuel Oil', 'CommodityEmissionFactor_CO2'].iloc[0] * 0.1

                    os.remove(path_CCS_CommOut)
                    CCS_all = [unit_row, CommOut_base, CCS_CommOut]
                    CCS_CommOut_final = pd.concat(CCS_all, ignore_index = True)
                    CCS_CommOut_final.to_csv(path_CCS_CommOut, index=False)

                    # modify ExistingCapacity.csv by adding "CCS " to CO2 emission technologies
                    path_existing_capacity = (
                        scenario_path_final
                        + "/technodata/power/ExistingCapacity.csv"
                    )

                    existing_capacity_base = self.existing_capacity_input.copy().drop(0)
                    CCS_existing_capacity = self.existing_capacity_input.copy()
                    unit_row = pd.read_csv(path_existing_capacity, nrows=1)

                    CCS_existing_capacity = CCS_existing_capacity.loc[CCS_existing_capacity.ProcessName.isin(CCS_tech)]
                    # add "CCS " to the beginning of the values in the "ProcessName" column
                    CCS_existing_capacity.loc[CCS_existing_capacity["ProcessName"].isin(CCS_tech), "ProcessName"] = 'CCS ' + CCS_existing_capacity.loc[CCS_existing_capacity["ProcessName"].isin(CCS_tech), "ProcessName"].astype(str)

                    os.remove(path_existing_capacity)
                    CCS_existing_capacity_final = pd.concat([unit_row, existing_capacity_base, CCS_existing_capacity], ignore_index = True)
                    CCS_existing_capacity_final.to_csv(path_existing_capacity, index=False)

                    # modify Technodata.csv by adding "CCS " to CO2 emission technologies
                    path_technodata = (
                        scenario_path_final
                        + "/technodata/power/Technodata.csv"
                    )

                    technodata_base = self.technodata_input.copy().drop(0)
                    CCS_technodata = self.technodata_input.copy()
                    unit_row = pd.read_csv(path_technodata, nrows=1)

                    CCS_technodata = CCS_technodata.loc[CCS_technodata.ProcessName.isin(CCS_tech)]
                    # add "CCS " to the beginning of the values in the "ProcessName" column
                    CCS_technodata.loc[CCS_technodata["ProcessName"].isin(CCS_tech), "ProcessName"] = 'CCS ' + CCS_technodata.loc[CCS_technodata["ProcessName"].isin(CCS_tech), "ProcessName"].astype(str)

                    os.remove(path_technodata)
                    CCS_technodata_final = pd.concat([unit_row, technodata_base, CCS_technodata], ignore_index = True)
                    CCS_technodata_final.to_csv(path_technodata, index=False)

                    # modify TechnodataTimeslices.csv by adding "CCS " to CO2 emission technologies
                    path_timeslices = (
                        scenario_path_final
                        + "/technodata/power/TechnodataTimeslices.csv"
                    )

                    timeslices_base = self.timeslices_input.copy().drop(0)
                    CCS_timeslices = self.timeslices_input.copy()
                    unit_row = pd.read_csv(path_timeslices, nrows=1)

                    CCS_timeslices = CCS_timeslices.loc[CCS_timeslices.ProcessName.isin(CCS_tech)]
                    # add "CCS " to the beginning of the values in the "ProcessName" column
                    CCS_timeslices.loc[CCS_timeslices["ProcessName"].isin(CCS_tech), "ProcessName"] = 'CCS ' + CCS_timeslices.loc[CCS_timeslices["ProcessName"].isin(CCS_tech), "ProcessName"].astype(str)

                    os.remove(path_timeslices)
                    CCS_timeslices_final = pd.concat([unit_row, timeslices_base, CCS_timeslices], ignore_index = True)
                    CCS_timeslices_final.to_csv(path_timeslices, index=False)

                path_techno_data = (
                    scenario_path_final
                    + "/technodata/power/Technodata.csv"
                )

                technodata = pd.read_csv(path_techno_data)
                unit_row = pd.read_csv(path_techno_data, nrows=1)

                technodata_final = technodata.copy().drop(0)

                if "costs" in scenario_path_final:
                    # change costs
                    technodata_final["cap_par"] = technodata_final["cap_par"].astype(float)
                    technodata_final["fix_par"] = technodata_final["fix_par"].astype(float)
                    

                    technodata_final["cap_par"].loc[
                        technodata_final.ProcessName.isin(fossil)
                    ] = random.uniform(
                        technodata_final["cap_par"] * 0.7, technodata_final["cap_par"] * 1.3
                    )
                    
                    technodata_final["fix_par"].loc[
                        technodata_final.ProcessName.isin(fossil)
                    ] = random.uniform(
                        technodata_final["fix_par"] * 0.7, technodata_final["fix_par"] * 1.3
                    )

                    technodata_final["cap_par"].loc[
                        technodata_final.ProcessName.isin(renewables)
                    ] = random.uniform(
                        technodata_final["cap_par"] * 0.7, technodata_final["cap_par"] * 1.3
                    )

                    technodata_final["fix_par"].loc[
                        technodata_final.ProcessName.isin(renewables)
                    ] = random.uniform(
                        technodata_final["fix_par"] * 0.7, technodata_final["fix_par"] * 1.3
                    )

                if "lifetime" in scenario_path_final:
                    # change lifetime
                    technodata_final["TechnicalLife"] = technodata_final["TechnicalLife"].astype(float)

                    technodata_final["TechnicalLife"].loc[
                        technodata_final.ProcessName.isin(fossil)
                    ] = random.uniform(
                        technodata_final["TechnicalLife"] * 0.7, technodata_final["TechnicalLife"] * 1.3
                    )

                    technodata_final["TechnicalLife"].loc[
                        technodata_final.ProcessName.isin(renewables)
                    ] = random.uniform(
                        technodata_final["TechnicalLife"] * 0.7, technodata_final["TechnicalLife"] * 1.3
                    )
                
                if "utilisationFactor" in scenario_path_final:                           
                    # change utilisation factor
                    technodata_final["UtilizationFactor"] = technodata_final["UtilizationFactor"].astype(float)

                    utilisation_min_fossil = technodata_final["UtilizationFactor"].loc[technodata_final.ProcessName.isin(fossil)] * 0.7
                    utilisation_max_fossil = technodata_final["UtilizationFactor"].loc[technodata_final.ProcessName.isin(fossil)] * 1.3
                    utilisation_capped_fossil = utilisation_max_fossil.where(utilisation_max_fossil <= 1, 1)
                    random_utilisation_fossil = np.random.uniform(utilisation_min_fossil, utilisation_capped_fossil)

                    utilisation_min_renewables = technodata_final["UtilizationFactor"].loc[technodata_final.ProcessName.isin(renewables)] * 0.7
                    utilisation_max_renewables = technodata_final["UtilizationFactor"].loc[technodata_final.ProcessName.isin(renewables)] * 1.3
                    utilisation_capped_renewables = utilisation_max_renewables.where(utilisation_max_renewables <= 1, 1)
                    random_utilisation_renewables = np.random.uniform(utilisation_min_renewables, utilisation_capped_renewables)

                    technodata_final.loc[technodata_final.ProcessName.isin(fossil), "UtilizationFactor"] = random_utilisation_fossil
                    technodata_final.loc[technodata_final.ProcessName.isin(renewables), "UtilizationFactor"] = random_utilisation_renewables
                
                if "capacity" in scenario_path_final:
                    if "capacityThirty" in scenario_path_final:
                        capacity_shut_down = ["2030", "2035", "2040", "2045", "2050"]
                    if "capacityForty" in scenario_path_final:
                        capacity_shut_down = ["2040", "2045", "2050"]
                    # change capacity
                    technodata_final["MaxCapacityAddition"] = technodata_final["MaxCapacityAddition"].astype(float)
                    technodata_final["MaxCapacityGrowth"] = technodata_final["MaxCapacityGrowth"].astype(float)

                    technodata_final["MaxCapacityAddition"].loc[technodata_final.ProcessName.isin(fossil) & technodata_final.Time.isin(capacity_shut_down)] = 0 
                    technodata_final["MaxCapacityGrowth"].loc[technodata_final.ProcessName.isin(fossil) & technodata_final.Time.isin(capacity_shut_down)] = 0

                # save new technodata file with all changes
                os.remove(path_techno_data)
                technodata_final = pd.concat([unit_row, technodata_final], ignore_index = True)
                technodata_final.to_csv(path_techno_data, index=False)

                if "energyDemand" in scenario_path_final:
                    # change energy demand
                    path_demand_2030 = (
                        scenario_path_final
                        + "/technodata/preset/Electricity2030Consumption.csv"
                    )

                    demand_2030_final = self.demand_2030_input.copy().drop(0)
                    unit_row_demand = pd.read_csv(path_demand_2030, nrows=1)

                    demand_2030_final["electricity"] = demand_2030_final["electricity"].astype(float)
                    
                    demand_2030_final["electricity"] = random.uniform(
                        demand_2030_final["electricity"] * 0.7, demand_2030_final["electricity"] * 1.3
                    )

                    os.remove(path_demand_2030)
                    demand_2030_final = pd.concat([unit_row_demand, demand_2030_final], ignore_index = True)

                    demand_2030_final = demand_2030_final.drop('Unnamed: 0', axis=1) # delete first row "Unnamed: 0" from base input 
                    demand_2030_final.to_csv(path_demand_2030, index=False)

                    path_demand_2040 = (
                        scenario_path_final
                        + "/technodata/preset/Electricity2040Consumption.csv"
                    )

                    demand_2040_final = self.demand_2040_input.copy().drop(0)
                    unit_row_demand = pd.read_csv(path_demand_2040, nrows=1)

                    demand_2040_final["electricity"] = demand_2040_final["electricity"].astype(float)
                    
                    demand_2040_final["electricity"] = random.uniform(
                        demand_2040_final["electricity"] * 0.7, demand_2040_final["electricity"] * 1.3
                    )

                    os.remove(path_demand_2040)
                    demand_2040_final = pd.concat([unit_row_demand, demand_2040_final], ignore_index = True)

                    demand_2040_final = demand_2040_final.drop('Unnamed: 0', axis=1) # delete first row "Unnamed: 0" from base input 
                    demand_2040_final.to_csv(path_demand_2040, index=False)

                    path_demand_2050 = (
                        scenario_path_final
                        + "/technodata/preset/Electricity2050Consumption.csv"
                    )

                    demand_2050_final = self.demand_2050_input.copy().drop(0)
                    unit_row_demand = pd.read_csv(path_demand_2050, nrows=1)

                    demand_2050_final["electricity"] = demand_2050_final["electricity"].astype(float)
                    
                    demand_2050_final["electricity"] = random.uniform(
                        demand_2050_final["electricity"] * 0.7, demand_2050_final["electricity"] * 1.3
                    )

                    os.remove(path_demand_2050)
                    demand_2050_final = pd.concat([unit_row_demand, demand_2050_final], ignore_index = True)

                    demand_2050_final = demand_2050_final.drop('Unnamed: 0', axis=1) # delete first row "Unnamed: 0" from base input 
                    demand_2050_final.to_csv(path_demand_2050, index=False)
                
                if any(scenario in scenario_path_final for scenario in ['C30-const', 'C80-const', 'C30-gr5', 'C80-gr5']):
                    # implement carbon price

                    path_carbon_price = (
                        scenario_path_final
                        + "/input/Projections.csv"
                    )

                    carbon_price = self.carbon_price_input.copy().drop(0)
                    unit_row = pd.read_csv(path_carbon_price, nrows=1)

                    carbon_price = self.carbon_price_input.copy().drop(0)
                    carbon_price["CO2f"] = carbon_price["CO2f"].astype(float)
                    carbon_price["Time"] = carbon_price["Time"].astype(int)

                    if 'C30-const' in scenario_path_final:
                        carbon_price.loc[carbon_price['Time'] >= 2025, 'CO2f'] = 0.03 # changes all values > 2025 to 0.03
                    elif 'C80-const' in scenario_path_final:
                        carbon_price.loc[carbon_price['Time'] >= 2025, 'CO2f'] = 0.08 # changes all values > 2025 to 0.08
                    elif 'C30-gr5' in scenario_path_final:
                        value = 0.03 * (1.05 ** (carbon_price['Time'] - 2040))
                        carbon_price.loc[carbon_price['Time'] >= 2025, 'CO2f'] = value.where((carbon_price['Time'] >= 2025))
                    elif 'C80-gr5' in scenario_path_final:
                        value = 0.08 * (1.05 ** (carbon_price['Time'] - 2040))
                        carbon_price.loc[carbon_price['Time'] >= 2025, 'CO2f'] = value.where((carbon_price['Time'] >= 2025))
                    else:
                        raise ValueError('Scenario not recognized.')

                    os.remove(path_carbon_price)
                    carbon_price_final = pd.concat([unit_row, carbon_price], ignore_index = True)
                    carbon_price_final.to_csv(path_carbon_price, index=False)

        return self


PATH_BASE_INPUT = "/Users/lilly/muse_kenya/run/Kenya/base/technodata/power"
PATH_DEMAND_INPUT = "/Users/lilly/muse_kenya/run/Kenya/base/technodata/preset"
PATH_PROJECTIONS_INPUT = "/Users/lilly/muse_kenya/run/Kenya/base/input"
PATH_COMMODITY_INPUT = "/Users/lilly/muse_kenya/run/Kenya/base/input"
scenario_input = Scenarios(
    path_to_base_input=os.path.join(PATH_BASE_INPUT, "Technodata.csv"),
    path_to_demand_2030=os.path.join(PATH_DEMAND_INPUT, "Electricity2030Consumption.csv"),
    path_to_demand_2040=os.path.join(PATH_DEMAND_INPUT, "Electricity2040Consumption.csv"),
    path_to_demand_2050=os.path.join(PATH_DEMAND_INPUT, "Electricity2050Consumption.csv"),
    path_carbon_price_input=os.path.join(PATH_PROJECTIONS_INPUT, "Projections.csv"),
    path_CCS_CommIn_input=os.path.join(PATH_BASE_INPUT, "CommIn.csv"),
    path_CCS_CommOut_input=os.path.join(PATH_BASE_INPUT, "CommOut.csv"),
    path_commodity_input=os.path.join(PATH_COMMODITY_INPUT, "GlobalCommodities.csv"),
    path_existing_capacity_input=os.path.join(PATH_BASE_INPUT, "ExistingCapacity.csv"),
    path_technodata_input=os.path.join(PATH_BASE_INPUT, "Technodata.csv"),
    path_timeslices_input=os.path.join(PATH_BASE_INPUT, "TechnodataTimeslices.csv"),
)

final_frame = scenario_input.scenario_generation()
