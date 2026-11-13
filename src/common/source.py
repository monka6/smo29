import random
from common.entities import LogEntry

class Source:
    def __init__(self, source_id, lambda_val):
        self.id = source_id
        self.lambda_val = lambda_val
        self.next_generation_time = 0.0
        self.generated_count = 0

    def generate_log(self, current_time):
        self.generated_count += 1
        log = LogEntry(log_id=self.generated_count, source_id=self.id, created_at=current_time)
        self.next_generation_time = current_time + random.expovariate(self.lambda_val)
        return log