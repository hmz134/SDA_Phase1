Generic Concurrent Real-Time Pipeline - Phase 3
================================================

MAIN FILE
---------
    python main.py

DATA FILE
---------
Place your dataset CSV in the data/ folder.
Update "dataset_path" in config.json to point to it.

    data/
        your_dataset.csv

CONFIG FILE
-----------
config.json is at the root next to main.py.

    dataset_path           - path to your csv file
    pipeline_dynamics      - speed, parallelism, queue sizes
    schema_mapping         - maps your csv columns to internal generic names
                             includes target_entity and column definitions
    processing             - supports two formats:
      (a) flat format      - operation + running_average_window_size
      (b) nested format    - stateless_tasks (verification) + stateful_tasks (avg)
    visualizations         - telemetry bars and chart definitions

HOW TO PLUG IN A NEW DATASET
-----------------------------
1. Put your csv in data/
2. In config.json set "dataset_path" to your file
3. In "schema_mapping" -> "columns", map each csv column to:
      entity_name    - the entity identifier (e.g. sensor ID, country)
      time_period    - the time column (e.g. timestamp, year)
      metric_value   - the numeric value to process
      security_hash  - the authentication signature column (if applicable)
4. Set "data_type" for each: string, integer, or float
5. If using signature verification, set "secret_key" and "iterations"
   in stateless_tasks
6. Run: python main.py

PIPELINE ARCHITECTURE
---------------------
The pipeline auto-detects its mode from config:

Mode A (with signature verification):
  Input (CSV) --> raw_queue --> [CoreWorkers x N: verify signature]
              --> verified_queue --> [Aggregator x 1: running average]
              --> processed_queue --> Dashboard

Mode B (without signature verification):
  Input (CSV) --> raw_queue --> [CoreWorkers x N: running average]
              --> processed_queue --> Dashboard

- CoreWorkers run in parallel (Scatter pattern)
- Aggregator gathers results (Gather pattern) when in Mode A
- Functional Core, Imperative Shell: shell owns the deque window,
  pure function computes average
- Observer Pattern: PipelineTelemetry polls queues and notifies dashboard

PROJECT STRUCTURE
-----------------
    main.py              - entry point and orchestrator
    config.json          - all configuration
    telemetry.py         - observer pattern subject
    readme.txt           - this file
    core/
        contracts.py     - protocols (TelemetryObserver)
        engine.py        - CoreWorker + Aggregator + pure functions
    plugins/
        inputs.py        - generic csv reader (Input Module)
        outputs.py       - real-time dashboard (Output/Observer)
    data/
        sample_sensor_data.csv

REQUIRED LIBRARIES
------------------
    pip install pandas matplotlib
