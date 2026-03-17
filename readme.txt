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
    processing
      stateless_tasks      - signature verification settings (algorithm, key, iterations)
      stateful_tasks       - running average settings (window size)
    visualizations         - telemetry bars and chart definitions

HOW TO PLUG IN A NEW DATASET
-----------------------------
1. Put your csv in data/
2. In config.json set "dataset_path" to your file
3. In "schema_mapping" -> "columns", map each csv column to:
      entity_name    - the entity identifier (e.g. sensor ID, country)
      time_period    - the time column (e.g. timestamp, year)
      metric_value   - the numeric value to process
      security_hash  - the authentication signature column
4. Set "data_type" for each: string, integer, or float
5. Update "secret_key" and "iterations" in stateless_tasks if needed
6. Run: python main.py

PIPELINE ARCHITECTURE
---------------------
Input (CSV) --> raw_queue --> [CoreWorkers x N: verify signature] 
            --> verified_queue --> [Aggregator x 1: running average]
            --> processed_queue --> Dashboard

- CoreWorkers run in parallel (Scatter pattern) - stateless signature check
- Aggregator gathers results (Gather pattern) - stateful running average
- Functional Core, Imperative Shell: shell owns the deque window, pure function computes average
- Observer Pattern: PipelineTelemetry polls queues and notifies dashboard

PROJECT STRUCTURE
-----------------
    main.py              - entry point and orchestrator
    config.json          - all configuration
    telemetry.py         - observer pattern subject
    readme.txt           - this file
    core/
        contracts.py     - protocols
        engine.py        - CoreWorker + Aggregator
    plugins/
        inputs.py        - generic csv reader
        outputs.py       - real-time dashboard (observer)
    data/
        sample_sensor_data.csv

REQUIRED LIBRARIES
------------------
    pip install pandas matplotlib
