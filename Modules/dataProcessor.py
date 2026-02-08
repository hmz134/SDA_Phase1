import pandas as pd


def clean(df):
    # year and value
    df = df.copy()

    df['Year'] = list(map(lambda x: pd.to_numeric(x, errors='coerce'), df['Year']))
    df['Value'] = list(map(lambda x: pd.to_numeric(x, errors='coerce'), df['Value']))

    df = df.dropna(subset=['Year', 'Value'])

    df['Year'] = df['Year'].astype(int)

    return df


def filter_data(df, region=None, year=None, country=None):
    if region:
        df = df[df['Region'] == region]

    if year:
        df = df[df['Year'] == year]

    if country:
        df = df[df['Country Name'] == country]

    return df


def avg(values): 
    if not values:
        return 0

    return sum(values) / len(values)


def total(values):
    if not values:
        return 0

    return sum(values)


def calc(df, op): #takes values from the filtered data and performs the required statistical operations
    values = list(filter(lambda x: pd.notna(x), df['Value'].tolist()))

    if op == 'average':
        return avg(values)

    if op == 'sum':
        return total(values)

    return 0


def region_sum(df):
    # gdp per region
    regions = df['Region'].unique()

    result = {
        r: sum(filter(lambda x: pd.notna(x),
                      df[df['Region'] == r]['Value'].tolist()))
        for r in regions
    }

    return result


def year_trend(df, region=None): # gdp per year
    if region:
        df = df[df['Region'] == region]

    years = sorted(df['Year'].unique())

    result = {
        int(y): sum(filter(lambda x: pd.notna(x),
                           df[df['Year'] == y]['Value'].tolist()))
        for y in years
    }

    return result


def formatNum(num):
    # format big numbers
    if num >= 1e12:
        return f"${num/1e12:.2f}T"

    if num >= 1e9:
        return f"${num/1e9:.2f}B"

    if num >= 1e6:
        return f"${num/1e6:.2f}M"

    return f"${num:,.2f}"
