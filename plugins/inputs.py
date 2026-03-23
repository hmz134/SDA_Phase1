import pandas as pd
import time


class GenericCSVReader:
    def __init__(self, raw_queue, cfg):
        self.raw_queue = raw_queue
        self.cfg = cfg

    def run(self):
        path = self.cfg['dataset_path']
        schema = self.cfg['schema_mapping']
        delay = self.cfg['pipeline_dynamics']['input_delay_seconds']

        df = pd.read_csv(path)

        # map source column names to internal generic names
        col_map = {c['source_name']: c['internal_mapping'] for c in schema['columns']}
        type_map = {c['internal_mapping']: c['data_type']   for c in schema['columns']}

        existing = [c for c in col_map if c in df.columns]
        df = df[existing].rename(columns=col_map)

        # coerce all numeric columns - bad values become NaN
        for col, dtype in type_map.items():
            if col not in df.columns:
                continue
            if dtype in ('integer', 'float'):
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # drop rows where ANY numeric column failed to cast - no silent 0 injection
        numeric_cols = [
            c['internal_mapping'] for c in schema['columns']
            if c['data_type'] in ('integer', 'float') and
            c['internal_mapping'] in df.columns
        ]
        df = df.dropna(subset=numeric_cols)

        # now safe to cast integers properly after bad rows are gone
        for col, dtype in type_map.items():
            if col in df.columns and dtype == 'integer':
                df[col] = df[col].astype(int)

        # use to_dict not iterrows - iterrows silently upcasts ints to floats
        records = df.to_dict('records')

        # push packets one by one - queue blocks naturally if full (backpressure)
        for packet in records:
            self.raw_queue.put(packet)
            time.sleep(delay)

        # one sentinel per worker so each knows when to stop
        n_workers = self.cfg['pipeline_dynamics']['core_parallelism']
        for _ in range(n_workers):
            self.raw_queue.put(None)
