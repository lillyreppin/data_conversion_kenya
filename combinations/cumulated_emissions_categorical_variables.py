import pandas as pd

def read_file_to_dataframe(filepath):
    return pd.read_csv(filepath)

# Calculate cumulated emissions from all technologies
def summarise_emissions_total(df):
    total_emission_cols = [col for col in df.columns if "Total Emissions" in col]
    df["Total emissions overall"] = df[total_emission_cols].sum(axis=1)
    print("Summarised emissions overall calculated and added successfully!")
    return df

# Calculate emissions in 2050 from all technologies
def summarise_emissions_2050(df):
    emission_2050_cols = [col for col in df.columns if "CO2f" in col]
    df["Total emissions 2050"] = df[emission_2050_cols].sum(axis=1)
    print("Summarised emissions for 2050 calculated and added successfully!")
    return df

# Define implementation of ccs technologies, carbonpricing and variation of demand as categorical variables
def add_ccs_carbonpricing_demand(df):
    df['ccs'] = df['scenario'].apply(lambda x: 1 if 'ccs' in x.lower() else 0)
    df['carbonpricing'] = df['scenario'].apply(lambda x: 1 if 'carbonpricing' in x.lower() else 0)
    df['demand'] = df['scenario'].apply(lambda x: 1 if 'demand' in x.lower() else 0)
    print("CCS, carbonpricing and demand determined successfully!")
    return df

# Define capacity limitation of exhaustible resources as categorical variable
def add_capacity_limitation(df):
    df['capacity limitation - exhausted'] = df['scenario'].apply(lambda x: 1 if 'capacity' in x.lower() else 0)
    print("Capacity limitation determined successfully!")
    return df

# Add new columns to existing dataframe
def write_dataframe_to_file(df, filepath):
    df.to_csv(filepath, index=False)

# Specify the file names
input_file = '/../../..'
output_file = '/../../..'

# Read the input file into a DataFrame
df = read_file_to_dataframe(input_file)

# Modify the DataFrame
df = summarise_emissions_total(df)
#df = summarise_emissions_2050(df)
df = add_ccs_carbonpricing_demand(df)
df = add_capacity_limitation(df)

# Write the DataFrame to the output file
write_dataframe_to_file(df, output_file)