import os
import pandas as pd

# Set the path to the main directory containing the scenario folders
main_directory = '/../../../'

# Set the output file path
output_file = '/../../../'

# Set the desired years
years = ['2020', '2025', '2030', '2040', '2050']

# List to store the extracted data
data = []

# Set to store the unique technologies
technologies = set()

# Iterate over each scenario directory
for scenario in os.listdir(main_directory):
    scenario_directory = os.path.join(main_directory, scenario)
    print(scenario)

    # Check if the scenario directory is valid
    if os.path.isdir(scenario_directory):

        # Iterate over each additional folder within the scenario directory
        for additional_folder in os.listdir(scenario_directory):
            additional_folder_path = os.path.join(scenario_directory, additional_folder)
            print(additional_folder)
            if os.path.isdir(additional_folder_path):

                # Check if the additional folder has the desired output files
                supply_file = os.path.join(additional_folder_path, 'results', 'MCAMetric_Supply.csv')
                technodata_file = os.path.join(additional_folder_path, 'technodata', 'power', 'Technodata.csv')

                if os.path.isfile(technodata_file) and os.path.isfile(supply_file):

                    # Read the technodata and supply data into pandas dataframes
                    technodata_df = pd.read_csv(technodata_file)
                    supply_df = pd.read_csv(supply_file)
                    
                    # Extract unique technologies from technodata and supply dataframes
                    technodata_technologies = set(technodata_df['ProcessName'].unique())
                    supply_technologies = set(supply_df['technology'].unique())

                    # Update the set of technologies
                    technologies.update(technodata_technologies - {'Unit'})
                    technologies.update(supply_technologies - technodata_technologies - {'Unit'})

                    # Extract and summarize data from the technodata and supply dataframes
                    scenario_data = {'scenario': scenario}
                    for year in years:
                        for technology in technologies:

                            # Filter the technodata dataframe for the current year and technology
                            technodata_filtered = technodata_df[(technodata_df['Time'] == year) & (technodata_df['ProcessName'] == technology)]
                            # Filter the supply dataframe for the current year and technology
                            supply_filtered = supply_df[(supply_df['year'].astype(str).str.split('.').str[0] == year) & (supply_df['technology'] == technology)]

                            # Summarize the technodata and supply data and add it to the scenario data dictionary
                            scenario_data.update({
                                f'Capital costs - {technology} - {year}': technodata_filtered['cap_par'].sum(),
                                f'Fixed costs - {technology} - {year}': technodata_filtered['fix_par'].sum(),
                                f'Lifetime - {technology} - {year}': technodata_filtered['TechnicalLife'].sum(),
                                f'Utilisation - {technology} - {year}': technodata_filtered['UtilizationFactor'].sum(),
                                f'MaxCapacityAddition - {technology} - {year}': technodata_filtered['MaxCapacityAddition'].sum(),
                                f'MaxCapacityGrowth - {technology} - {year}': technodata_filtered['MaxCapacityGrowth'].sum(),
                                f'Electricity - {technology} - {year}': supply_filtered[supply_filtered['commodity'] == 'electricity']['supply'].sum(),
                                f'CO2f - {technology} - {year}': supply_filtered[supply_filtered['commodity'] == 'CO2f']['supply'].sum(),
                            })

                    # Append the scenario data to the list
                    data.append(scenario_data)

# Sort the technologies alphabetically
sorted_technologies = sorted(technologies)

# Convert the list of dictionaries to a dataframe
df = pd.DataFrame(data)

# Reorder the columns of the dataframe
df = df[['scenario'] + [f'{metric} - {tech} - {year}' for metric in ['Capital costs', 'Fixed costs', 'Lifetime', 'Utilisation', 'MaxCapacityAddition', 'MaxCapacityGrowth', 'Electricity', 'CO2f'] for tech in sorted_technologies for year in years]]

# Write the dataframe to the output file
df.to_csv(output_file, index=False)