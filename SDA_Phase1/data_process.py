
import pandas as pd

# load
df = pd.read_excel('gdp_with_continent_filled.xlsx')

id_vars = ['Country Name', 'Country Code','Indicator Name','Indicator Code', 'Continent']
year_columns = [col for col in df.columns if isinstance(col, int)]

df_long = pd.melt(df,id_vars=id_vars, value_vars=year_columns, var_name='Year',
                  value_name='GDP_Value')

df_long = df_long.rename(columns={ 'continent': 'region', 'GDP Value': 'value' })

# select col
df_final = df_long[['Country name','region','year','value']]

df_final = df_final.dropna(subset=['Value'])

# save as csv
df_final.to_csv('data/gdp_data.csv', index=False)

print("converted to csv\n")
print(f"Records created: {len(df_final)}")
print(f"output file: data/gdp_data.csv")