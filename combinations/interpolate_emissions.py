import pandas as pd
import numpy as np

# Load the CSV file
df = pd.read_csv("/../../..")

# Convert all NaN values to 0.0
df.fillna(0.0, inplace=True)

# Process for each technology
technologies = ["CCS Biomass Power Plant",
            "CCS Coal Power Plant",
            "CCS Gas Power Plant (SCGT)",
            "CCS Gas Power Plant (CCGT)",
            "CCS Light Fuel Oil Power Plant",
            "CCS Light Fuel Oil Standalone Generator (1kW)",
            "CCS Oil Fired Gas Turbine (SCGT)",
            "Coal Power Plant",
            "Gas Power Plant (SCGT)",
            "Gas Power Plant (CCGT)",
            "Light Fuel Oil Power Plant",
            "Light Fuel Oil Standalone Generator (1kW)",
            "Oil Fired Gas Turbine (SCGT)",
            "Biomass Power Plant",
]

for tech in technologies:
    # Filter columns related to the current technology
    cols = [col for col in df.columns if 'CO2f - ' + tech in col]
    sub_df = df[cols]
    
    # Sort columns in increasing order of years (assuming they end with the year)
    cols_sorted = sorted(cols, key=lambda x: int(x.split(' - ')[-1]))
    sub_df = sub_df[cols_sorted]
    
    # Linear interpolation for missing years
    for i, col in enumerate(cols_sorted):
        year = int(col.split(' - ')[-1])
        if i < len(cols_sorted) - 1:
            next_year = int(cols_sorted[i+1].split(' - ')[-1])
            years_diff = next_year - year
            if years_diff > 1:
                # Compute slopes for linear interpolation
                slopes = (sub_df[cols_sorted[i+1]] - sub_df[col]) / years_diff
                for j in range(1, years_diff):
                    # Create new columns for missing years
                    new_col = col[:-4] + str(year + j)
                    sub_df[new_col] = sub_df[col] + slopes * j
                    # Add the new column to the original DataFrame
                    df[new_col] = sub_df[new_col]
    # Calculate the total emissions for all years (existing + interpolated) for each scenario
    df[tech + ' Total Emissions'] = sub_df.sum(axis=1)

# Save the results to the original CSV file
df.to_csv('...', index=False)
