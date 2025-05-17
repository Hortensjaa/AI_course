from time import time


class Timer:
    def __init__(self, interval: float):
        self.interval = interval
        self.last_time = time()

    def reset(self):
        self.last_time = time()

    def ready(self) -> bool:
        return time() - self.last_time >= self.interval
