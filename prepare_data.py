import pandas as pd

# load
df = pd.read_excel('data/gdp_with_continent_filled.xlsx')

id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code', 'Continent']
year_columns = [col for col in df.columns if isinstance(col, int)]

df_long = pd.melt(df, id_vars=id_vars, value_vars=year_columns, var_name='Year',
                  value_name='Value')

# rename Continent to Region
df_long = df_long.rename(columns={'Continent': 'Region'})

# select col
df_final = df_long[['Country Name', 'Region', 'Year', 'Value']]
df_final = df_final.dropna(subset=['Value'])

# save as csv
df_final.to_csv('data/gdp_data.csv', index=False)

# save as json (needed for json input mode)
df_final.to_json('data/gdp_with_continent_filled.json', orient='records', indent=2)

print("converted to csv and json\n")
print(f"Records created: {len(df_final)}")
print(f"output files: data/gdp_data.csv, data/gdp_with_continent_filled.json")