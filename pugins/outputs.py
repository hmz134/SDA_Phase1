import matplotlib.pyplot as plt


def format_num(num):
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    if num >= 1e9:
        return f"${num/1e9:.2f}B"
    if num >= 1e6:
        return f"${num/1e6:.2f}M"
    return f"${num:,.2f}"


class ConsoleWriter:
    def write(self, records: list) -> None:
        print("\n========= GDP ANALYSIS DASHBOARD =========\n")

        for item in records:
            print(f"--- {item['label']} ---")
            data = item.get('data', {})

            t = item.get('type')

            if t in ('top10', 'bottom10'):
                for country, val in data.items():
                    print(f"  {country}: {format_num(val)}")

            elif t == 'growth_rate':
                for country, rate in data.items():
                    print(f"  {country}: {rate}%")

            elif t == 'avg_by_continent':
                for region, val in data.items():
                    print(f"  {region}: {format_num(val)}")

            elif t == 'global_trend':
                for year, val in data.items():
                    print(f"  {year}: {format_num(val)}")

            elif t == 'fastest_continent':
                fastest = data.get('fastest')
                print(f"  fastest growing: {fastest}")
                for region, rate in data.get('growth_rates', {}).items():
                    print(f"  {region}: {rate}%")

            elif t == 'declining':
                if data:
                    for country in data:
                        print(f"  {country}")
                else:
                    print("  no countries found with consistent decline")

            elif t == 'contribution':
                for region, pct in data.items():
                    print(f"  {region}: {pct}%")

            print()


class GraphicsChartWriter:
    def write(self, records: list) -> None:
        # create charts for each record
        for item in records:
            t = item.get('type')
            data = item.get('data', {})
            label = item.get('label', '')

            if t == 'top10':
                self._bar_chart(data, label, 'country', 'gdp (usd)', 'top10_gdp.png')

            elif t == 'bottom10':
                self._bar_chart(data, label, 'country', 'gdp (usd)', 'bottom10_gdp.png')

            elif t == 'growth_rate':
                self._bar_chart(data, label, 'country', 'growth rate (%)', 'growth_rate.png')

            elif t == 'avg_by_continent':
                self._bar_chart(data, label, 'continent', 'avg gdp (usd)', 'avg_by_continent.png')
                self._pie_chart(data, label, 'avg_by_continent_pie.png')

            elif t == 'global_trend':
                self._line_chart(data, label, 'year', 'total gdp (usd)', 'global_trend.png')

            elif t == 'fastest_continent':
                rates = data.get('growth_rates', {})
                self._bar_chart(rates, label, 'continent', 'growth rate (%)', 'fastest_continent.png')

            elif t == 'contribution':
                self._pie_chart(data, label, 'continent_contribution_pie.png')
                self._bar_chart(data, label, 'continent', 'contribution (%)', 'continent_contribution_bar.png')

        print("\ncharts saved")

    def _save_figure(self, filename):
        # save and close current figure
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

    def _bar_chart(self, data, title, xlabel, ylabel, filename):
        # make a simple bar chart
        keys = list(data.keys())
        vals = list(data.values())
        plt.figure(figsize=(10, 5))
        plt.bar(keys, vals)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha='right')
        self._save_figure(filename)

    def _pie_chart(self, data, title, filename):
        # make a simple pie chart
        labels = list(data.keys())
        vals = list(data.values())
        plt.figure(figsize=(8, 8))
        plt.pie(vals, labels=labels, autopct='%1.1f%%')
        plt.title(title)
        self._save_figure(filename)

    def _line_chart(self, data, title, xlabel, ylabel, filename):
        # make a simple line chart
        keys = list(data.keys())
        vals = list(data.values())
        plt.figure(figsize=(10, 5))
        plt.plot(keys, vals, marker='o')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        self._save_figure(filename)