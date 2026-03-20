# 🚀 Generic Concurrent Real-Time Pipeline — Phase 3

A high-throughput, domain-agnostic data processing system designed for real-time analysis and visualization of concurrent data streams.

## ⚡ Quick Start

### 1. Installation
Ensure you have the required dependencies:
```bash
pip install pandas matplotlib
```
### 2. Execution
Launch the pipeline from the project root:
```bash
python main.py
```

### 3. Customization
Drop any CSV into `data/`, map your columns in `config.json`, and the system handles the rest.

## 🏗️ System Architecture

The pipeline is built on a Producer-Consumer model using bounded multiprocessing.Queue to manage backpressure. It dynamically self-configures based on the available data attributes:

### Mode A: Secure Verifying Pipeline (3-Queue)
`Input (CSV)` ➔ `raw_queue` ➔ `[CoreWorkers x N: Signature Verification]` ➔ `verified_queue` ➔ `[Aggregator: Windowed Average]` ➔ `processed_queue` ➔ `Dashboard`

### Mode B: Direct Processing Pipeline (2-Queue)
`Input (CSV)` ➔ `raw_queue` ➔ `[CoreWorkers x N: Windowed Average]` ➔ `processed_queue` ➔ `Dashboard`

## 🌟 Technical Highlights

*   Dynamic Architecture Auto-scaling: Automatically provisions the optimal concurrency model based on the presence of security-statiteless tasks in the `config.json`.
*   Resilient Observer Pattern: A robust `PipelineTelemetry` subject monitors multi-process queue health and notifies the `RealTimeDashboard` observer for low-latency UI updates.
*   Dual-Format Configuration: Seamlessly parses both strict flat "spec-compliant" configurations and feature-rich nested JSON structures.
*   Functional Core, Imperative Shell: High-reliability design separating pure data transformations from mutable process states (sliding window `deque`).

## 🧑‍💻 Technical Team & Contributions
### Muhammad Hamza
*   Pipeline Orchestration: Engineered the central lifecycle management system and multi-process bootstrap logic.
*   Resilient Ingestion: Designed the schema-agnostic CSV reader capable of dynamic column mapping and data-type casting.
*   Queue Optimization: Tuned the bounded `multiprocessing` communication layer to ensure efficient backpressure and prevent memory overflow.
### Nauman Ali
*   Real-Time Telemetry: Developed the Observer-based monitoring system for cross-process health tracking.
*   Functional Core Development: Implemented the pure mathematical core for windowed averages and signature verification.
*   Visual Engineering: Crafted the high-performance Matplotlib dashboard with dynamic plotting and real-time backpressure indicators.

## 🛡️ Engineering Standards

*   Functional Paradigms: Heavy reliance on `map`, `filter`, `lambda`, and `reduce` for predictable data flows.
*   Dependency Inversion: Decoupled IO and logic using Python's Protocol-based structural subtyping.
*   Domain Agnostic: Zero hardcoded logic—every transformation and visualization property is injected via `config.json`.
