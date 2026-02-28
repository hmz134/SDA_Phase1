import pandas as pd
from core.contracts import DataSink


class TransformationEngine:
    def __init__(self, sink: DataSink, cfg: dict):
        self.sink = sink
        self.cfg = cfg

    def execute(self, raw_data: list) -> None:
        df = pd.DataFrame(raw_data)

        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.dropna(subset=['Year', 'Value'])
        df['Year'] = df['Year'].astype(int)

        continent = self.cfg.get('continent')
        year = self.cfg.get('year')
        year_start = self.cfg.get('year_range', [2000, 2020])[0]
        year_end = self.cfg.get('year_range', [2000, 2020])[1]
        decline_years = self.cfg.get('decline_years', 5)

        results = []

        # top 10 countries by gdp for continent and year
        results.append({
            'type': 'top10',
            'label': f'top 10 countries by gdp in {continent} ({year})',
            'data': top_10(df, continent, year)
        })

        # bottom 10 countries by gdp for continent and year
        results.append({
            'type': 'bottom10',
            'label': f'bottom 10 countries by gdp in {continent} ({year})',
            'data': bottom_10(df, continent, year)
        })

        # gdp growth rate per country in continent for date range
        results.append({
            'type': 'growth_rate',
            'label': f'gdp growth rate in {continent} ({year_start}-{year_end})',
            'data': growth_rate(df, continent, year_start, year_end)
        })

        # average gdp by continent for date range
        results.append({
            'type': 'avg_by_continent',
            'label': f'average gdp by continent ({year_start}-{year_end})',
            'data': avg_by_continent(df, year_start, year_end)
        })

        # total global gdp trend for date range
        results.append({
            'type': 'global_trend',
            'label': f'total global gdp trend ({year_start}-{year_end})',
            'data': global_gdp_trend(df, year_start, year_end)
        })

        # fastest growing continent for date range
        results.append({
            'type': 'fastest_continent',
            'label': f'fastest growing continent ({year_start}-{year_end})',
            'data': fastest_continent(df, year_start, year_end)
        })

        # countries with consistent gdp decline in last x years
        results.append({
            'type': 'declining',
            'label': f'countries with consistent gdp decline (last {decline_years} years)',
            'data': declining_countries(df, continent, decline_years)
        })

        # contribution of each continent to global gdp for date range
        results.append({
            'type': 'contribution',
            'label': f'continent contribution to global gdp ({year_start}-{year_end})',
            'data': continent_contribution(df, year_start, year_end)
        })

        # write results to sink
        self.sink.write(results)

def top_10(df, continent, year):
    sub = df[(df['Region'] == continent) & (df['Year'] == year)].dropna(subset=['Value'])
    sub = sub.sort_values('Value', ascending=False).head(10)
    return dict(zip(sub['Country Name'], sub['Value']))


def bottom_10(df, continent, year):
    sub = df[(df['Region'] == continent) & (df['Year'] == year)].dropna(subset=['Value'])
    sub = sub.sort_values('Value', ascending=True).head(10)
    return dict(zip(sub['Country Name'], sub['Value']))


def growth_rate(df, continent, year_start, year_end):
    sub = df[df['Region'] == continent]

    start = sub[sub['Year'] == year_start].set_index('Country Name')['Value']
    end = sub[sub['Year'] == year_end].set_index('Country Name')['Value']

    joined = start.to_frame('start').join(end.to_frame('end'), how='inner')
    joined = joined[joined['start'] > 0]

    countries = joined.index.tolist()

    # functional map over countries to compute rates
    rates = list(map(
        lambda c: round(((joined.loc[c, 'end'] - joined.loc[c, 'start']) / joined.loc[c, 'start']) * 100, 2),
        countries
    ))

    return dict(zip(countries, rates))


def avg_by_continent(df, year_start, year_end):
    sub = df[(df['Year'] >= year_start) & (df['Year'] <= year_end)]
    if sub.empty:
        return {}
    means = sub.groupby('Region')['Value'].mean().round(2).to_dict()
    return means


def global_gdp_trend(df, year_start, year_end):
    sub = df[(df['Year'] >= year_start) & (df['Year'] <= year_end)]
    if sub.empty:
        return {}
    sums = sub.groupby('Year')['Value'].sum().round(2)
    return {int(year): float(sums.loc[year]) for year in sums.index}


def fastest_continent(df, year_start, year_end):
    sub = df[(df['Year'] >= year_start) & (df['Year'] <= year_end)]
    continents = sub['Region'].dropna().unique().tolist()

    def continent_growth(r):
        s = sub[(sub['Region'] == r) & (sub['Year'] == year_start)]['Value'].sum()
        e = sub[(sub['Region'] == r) & (sub['Year'] == year_end)]['Value'].sum()
        return round(((e - s) / s) * 100, 2) if s != 0 else 0

    # functional map over continents
    growth_dict = dict(zip(continents, map(continent_growth, continents)))

    fastest = max(growth_dict, key=lambda k: growth_dict[k]) if growth_dict else None

    return {'fastest': fastest, 'growth_rates': growth_dict}


def declining_countries(df, continent, n_years):
    # list countries that show a strict decline each year for the last n years
    sub = df[df['Region'] == continent]
    if sub.empty:
        return []

    max_year = int(sub['Year'].max())
    years = list(range(max_year - n_years + 1, max_year + 1))
    countries = sub['Country Name'].dropna().unique().tolist()

    def is_declining(country):
        vals = list(map(
            lambda y: sub[(sub['Country Name'] == country) & (sub['Year'] == y)]['Value'].values,
            years
        ))

        vals_flat = list(filter(lambda v: len(v) > 0, vals))
        if len(vals_flat) < n_years:
            return False

        nums = list(map(lambda v: v[0], vals_flat))

        # check strict decline using all and map
        return all(map(lambda p: p[1] < p[0], zip(nums, nums[1:])))

    return list(filter(is_declining, countries))


def continent_contribution(df, year_start, year_end):
    sub = df[(df['Year'] >= year_start) & (df['Year'] <= year_end)]
    if sub.empty:
        return {}
    total = sub['Value'].sum()
    if total == 0:
        continents = sub['Region'].dropna().unique().tolist()
        return {r: 0.0 for r in continents}
    parts = sub.groupby('Region')['Value'].sum().to_dict()
    result = {r: round((parts.get(r, 0) / total) * 100, 2) for r in parts}
    return result