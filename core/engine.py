import hashlib
from collections import deque
from functools import reduce


# pure stateless - generates pbkdf2 signature for a given value
def generate_signature(raw_value_str: str, key: str, iterations: int, algorithm: str = 'sha256') -> str:
    password_bytes = key.encode('utf-8')
    salt_bytes = raw_value_str.encode('utf-8')
    hash_bytes = hashlib.pbkdf2_hmac(algorithm, password_bytes, salt_bytes, iterations)
    return hash_bytes.hex()


# value must be rounded to 2 decimals - same way the signature was originally made
def verify_packet(packet: dict, key: str, iterations: int, algorithm: str = 'sha256') -> bool:
    raw_value_str = f"{float(packet['metric_value']):.2f}"
    expected = generate_signature(raw_value_str, key, iterations, algorithm)
    return expected == packet.get('security_hash', '')


# pure functional core - sliding window average
def compute_average(window: deque) -> float:
    if not window:
        return 0.0
    total = reduce(lambda acc, x: acc + x, window)
    return round(total / len(window), 4)


# scatter worker - pulls from raw queue, drops anything that fails verification
class CoreWorker:
    def __init__(self, raw_queue, verified_queue, cfg):
        self.raw_queue = raw_queue
        self.verified_queue = verified_queue
        self.cfg = cfg

    def run(self):
        stateless = self.cfg['processing']['stateless_tasks']
        key = stateless['secret_key']
        iterations = stateless['iterations']
        hash_name = stateless.get('hash_name', 'sha256')

        while True:
            packet = self.raw_queue.get()

            if packet is None:  # kill signal - pass it along and stop
                self.verified_queue.put(None)
                break

            if verify_packet(packet, key, iterations, hash_name):
                self.verified_queue.put(packet)
            # fake packets just get dropped silently


# gather node - waits for all workers then computes running average
class Aggregator:
    def __init__(self, verified_queue, processed_queue, cfg, n_workers):
        self.verified_queue = verified_queue
        self.processed_queue = processed_queue
        self.cfg = cfg
        self.n_workers = n_workers

    def run(self):
        window_size = self.cfg['processing']['stateful_tasks']['running_average_window_size']

        # imperative shell owns the mutable window state
        window = deque(maxlen=window_size)
        done_count = 0

        while True:
            packet = self.verified_queue.get()

            if packet is None:
                done_count += 1
                if done_count >= self.n_workers:  # all workers finished
                    self.processed_queue.put(None)
                    break
                continue

            window.append(packet['metric_value'])

            # functional core - pure avg from window snapshot
            avg = compute_average(window)

            self.processed_queue.put({**packet, 'computed_metric': avg})