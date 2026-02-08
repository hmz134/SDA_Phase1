import matplotlib.pyplot as plt
from Modules.dataProcessor import formatNum


def show_header(cfg, info, result):
    print("\nGDP DASHBOARD")
    print("-------------")

    print("region:", cfg['region'])
    print("year:", cfg['year'])
    print("operation:", cfg['operation'])
    print("records:", info['total'])

    print("\nresult:",formatNum(result))


def make_charts(region_data, year_data):
    # region bar chart
    plt.figure()
    plt.bar(region_data.keys(), region_data.values())
    plt.title("gdp by region")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("region_gdp.png")
    plt.close()

    # yearly line chart
    plt.figure()
    plt.plot(year_data.keys(), year_data.values(), marker='o')
    plt.title("gdp over years")
    plt.xlabel("year")
    plt.ylabel("gdp")
    plt.tight_layout()
    plt.savefig("year_gdp.png")
    plt.close()

    print("\ncharts saved")

