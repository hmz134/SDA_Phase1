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

        # cast_map defines the conversion for each supported type
        # string columns are excluded
        cast_map = {
            'integer': lambda s: pd.to_numeric(s, errors='coerce').fillna(0).astype(int),
            'float': lambda s: pd.to_numeric(s, errors='coerce'),
        }

        # apply all type casts in one shot using assign + dict comprehension - no explicit loop
        df = df.assign(**{
            col: cast_map[dtype](df[col])
            for col, dtype in type_map.items()
            if col in df.columns and dtype in cast_map
        })

        df = df.dropna(subset=['metric_value'])

        # use to_dict not iterrows - iterrows silently upcasts ints to floats
        records = df.to_dict('records')

        # push packets one by one - queue blocks naturally if full (backpressure)
        list(map(lambda packet: (self.raw_queue.put(packet), time.sleep(delay)), records))

        # one sentinel per worker so each knows when to stop
        n_workers = self.cfg['pipeline_dynamics']['core_parallelism']
        list(map(lambda _: self.raw_queue.put(None), range(n_workers)))