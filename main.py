import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'Modules'))

from Modules.data_loader import load_config, check_config, load_data, data_info
from Modules.dataProcessor import clean, filter_data, calc
from Modules.dataProcessor import region_sum, year_trend
from Modules.dashboard import show_header, make_charts


def main():
    cfg = load_config()
    check_config(cfg)

    raw = load_data()
    data = clean(raw)

    info = data_info(data)

    filtered = filter_data(
        data,
        cfg['region'],
        cfg['year'],
        None
    )

    result = calc(filtered, cfg['operation'])

    regions = region_sum(data)
    years = year_trend(data, cfg['region'])

    if cfg['output'] == 'dashboard':
        show_header(cfg, info, result)
        make_charts(regions, years)
    else:
        print(result)


if __name__ == "__main__":
    main()

