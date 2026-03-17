# subject in the observer pattern
# polls queue sizes and notifies all attached observers
class PipelineTelemetry:

    def __init__(self, raw_queue, verified_queue, processed_queue, max_size):
        self.raw_queue       = raw_queue
        self.verified_queue  = verified_queue
        self.processed_queue = processed_queue
        self.max_size        = max_size
        self._observers      = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def poll(self):
        try:
            sizes = list(map(lambda q: q.qsize(),
                             (self.raw_queue, self.verified_queue, self.processed_queue)))
        except Exception:
            sizes = [0, 0, 0]

        list(map(lambda obs: obs.update(*sizes, self.max_size), self._observers))