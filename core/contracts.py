from typing import Protocol, List, Any, runtime_checkable


@runtime_checkable
class DataSink(Protocol):
    def write(self, records: List[dict]) -> None:
        ...


class PipelineService(Protocol):
    def execute(self, raw_data: List[Any]) -> None:
        ...


# observer - dashboard must implement this
class TelemetryObserver(Protocol):
    def update(self, raw_size: int, verified_size: int, proc_size: int, max_size: int) -> None:
        ...
