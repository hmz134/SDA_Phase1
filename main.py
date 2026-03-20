import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import multiprocessing

from core.engine import CoreWorker, Aggregator
from plugins.inputs import GenericCSVReader
from plugins.outputs import RealTimeDashboard
from telemetry import PipelineTelemetry


def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)


def check_config(cfg):
    for key in ['dataset_path', 'pipeline_dynamics', 'schema_mapping', 'processing', 'visualizations']:
        if key not in cfg:
            raise ValueError(f"missing config key: {key}")

    for key in ['input_delay_seconds', 'core_parallelism', 'stream_queue_max_size']:
        if key not in cfg['pipeline_dynamics']:
            raise ValueError(f"missing pipeline_dynamics key: {key}")

    proc = cfg['processing']
    # accept the spec flat format OR the nested stateless/stateful format
    has_flat = 'operation' in proc
    has_nested = 'stateless_tasks' in proc or 'stateful_tasks' in proc
    if not has_flat and not has_nested:
        raise ValueError("processing must have 'operation' or 'stateless_tasks'/'stateful_tasks'")


def count_input_rows(cfg):
    import pandas as pd
    # find the source column that maps to metric_value n count non-null rows
    metric_col = next(
        c['source_name'] for c in cfg['schema_mapping']['columns']
        if c['internal_mapping'] == 'metric_value'
    )
    df = pd.read_csv(cfg['dataset_path'])
    return int(df[metric_col].notna().sum())


def has_stateless(cfg):
    return 'stateless_tasks' in cfg['processing'] and cfg['processing']['stateless_tasks']


def bootstrap():
    cfg = load_config()
    check_config(cfg)

    max_size = cfg['pipeline_dynamics']['stream_queue_max_size']
    n_workers = cfg['pipeline_dynamics']['core_parallelism']

    total_input_rows = count_input_rows(cfg)

    raw_queue = multiprocessing.Queue(maxsize=max_size)  # input -> workers
    processed_queue = multiprocessing.Queue(maxsize=max_size)  # final -> dashboard

    reader = GenericCSVReader(raw_queue, cfg)

    if has_stateless(cfg):
        # 3 queue: raw -> workers (verify) -> verified -> aggregator (avg) -> processed
        verified_queue = multiprocessing.Queue(maxsize=max_size)
        workers = [CoreWorker(raw_queue, verified_queue, cfg) for _ in range(n_workers)]
        aggregator = Aggregator(verified_queue, processed_queue, cfg, n_workers)
        dashboard = RealTimeDashboard(processed_queue, cfg, total_input_rows)
        telemetry = PipelineTelemetry(raw_queue, verified_queue, processed_queue, max_size)
        telemetry.attach(dashboard)
        
        procs = [
            multiprocessing.Process(target=reader.run,     daemon=True),
            *[multiprocessing.Process(target=w.run, daemon=True) for w in workers],
            multiprocessing.Process(target=aggregator.run, daemon=True),
        ]
        queues = [raw_queue, verified_queue, processed_queue]
    else:
        # 2 queue raw -> workers (running avg) -> processed
        workers = [CoreWorker(raw_queue, processed_queue, cfg) for _ in range(n_workers)]
        dashboard = RealTimeDashboard(processed_queue, cfg, total_input_rows)
        telemetry = PipelineTelemetry(raw_queue, None, processed_queue, max_size)
        telemetry.attach(dashboard)
        procs = [
            multiprocessing.Process(target=reader.run, daemon=True),
            *[multiprocessing.Process(target=w.run, daemon=True) for w in workers],
        ]
        queues = [raw_queue, processed_queue]

    print("starting pipeline...")
    list(map(lambda p: p.start(), procs))

    # dashboard must run on the main thread
    try:
        dashboard.run(telemetry)
    finally:
        list(map(lambda q: q.cancel_join_thread(), queues))
        list(map(lambda p: p.join(timeout=3), procs))
        print("pipeline stopped")


if __name__ == '__main__':
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
        raise