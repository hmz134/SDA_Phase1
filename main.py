import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json

from core.engine import TransformationEngine
from plugins.inputs import CSVReader, JSONReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter

# map config strings to actual classes
INPUT_DRIVERS = {
    'csv': CSVReader,
    'json': JSONReader
}

OUTPUT_DRIVERS = {
    'console': ConsoleWriter,
    'charts': GraphicsChartWriter
}

# file paths for each input type
INPUT_PATHS = {
    'csv': 'data/gdp_data.csv',
    'json': 'data/gdp_with_continent_filled.json'
}


def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)


def check_config(cfg):
    needed = ['input', 'output','continent', 'year','year_range','decline_years']
    for key in needed:
        if key not in cfg:
            raise ValueError(f"missing config key: {key}")

    if cfg['input'] not in INPUT_DRIVERS:
        raise ValueError(f"input must be one of: {list(INPUT_DRIVERS.keys())}")

    if cfg['output'] not in OUTPUT_DRIVERS:
        raise ValueError(f"output must be one of: {list(OUTPUT_DRIVERS.keys())}")

    if len(cfg['year_range']) != 2:
        raise ValueError("year_range must have exactly 2 values: [start, end]")


def bootstrap():
    cfg = load_config()
    check_config(cfg)

    #instantiate output
    sink = OUTPUT_DRIVERS[cfg['output']]()

    # instantiate core engine
    engine = TransformationEngine(sink, cfg)

    # instantiate input 
    input_path = INPUT_PATHS[cfg['input']]
    reader = INPUT_DRIVERS[cfg['input']](engine, input_path)
    reader.run()


if __name__ == "__main__":
    try:
        bootstrap()
    except FileNotFoundError as e:
        print(f"file not found: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"config error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"something went wrong: {e}")
        sys.exit(1)