import pandas as pd
import json
import re
from core.contracts import PipelineService


class CSVReader:
    def __init__(self, service: PipelineService, path: str):
        self.service = service
        self.path = path

    def run(self):
        df = pd.read_csv(self.path)

        raw_data = df.to_dict(orient='records')
        self.service.execute(raw_data)


class JSONReader:
    def __init__(self, service: PipelineService, path: str):
        self.service = service
        self.path = path

    def run(self):
        with open(self.path, 'r') as f:
            text = f.read()

        text = re.sub(r'\bNaN\b', 'null', text)

        text = re.sub(r'#@\$!\\', 'null', text)

        raw_json = json.loads(text)

        df = pd.DataFrame(raw_json)

        # convert wide format to long format
        id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code', 'Continent']
        year_cols = [col for col in df.columns if str(col).isdigit()]

        df_long = pd.melt(
            df,
            id_vars=id_vars,
            value_vars=year_cols,
            var_name='Year',
            value_name='Value'
        )

        # rename and select columns
        df_long = df_long.rename(columns={'Continent': 'Region'})
        df_long = df_long[['Country Name', 'Region', 'Year', 'Value']]

        # remove missing values
        df_long = df_long.dropna(subset=['Value'])

        # convert to records and execute pipeline
        raw_data = df_long.to_dict(orient='records')
        self.service.execute(raw_data)