import random
from common.entities import LogEntry

class Source:
    def __init__(self, source_id, lambda_val):
        self.id = source_id
        self.lambda_val = lambda_val
        self.next_generation_time = 0.0
        self.generated_count = 0
        self.rejected_count = 0
        
        self.processed_count = 0
        self.sum_time_in_system = 0.0
        self.sum_waiting_time = 0.0
        self.sum_service_time = 0.0
        
        self.sum_sq_waiting_time = 0.0
        self.sum_sq_service_time = 0.0

    def generate_log(self, current_time):
        self.generated_count += 1
        log = LogEntry(log_id=self.generated_count, source_id=self.id, created_at=current_time)
        self.next_generation_time = current_time + random.expovariate(self.lambda_val)
        return log

    def add_statistics(self, time_in_system, waiting_time, service_time):
        self.processed_count += 1
        self.sum_time_in_system += time_in_system
        self.sum_waiting_time += waiting_time
        self.sum_service_time += service_time
        
        self.sum_sq_waiting_time += waiting_time ** 2
        self.sum_sq_service_time += service_time ** 2

    def get_next_time(self): return self.next_generation_time
    def get_generated_count(self): return self.generated_count
    def get_rejected_count(self): return self.rejected_count

    def get_prob_reject(self):
        return self.rejected_count / self.generated_count if self.generated_count > 0 else 0.0

    def get_avg_time_in_system(self):
        return self.sum_time_in_system / self.processed_count if self.processed_count > 0 else 0.0

    def get_avg_waiting_time(self):
        return self.sum_waiting_time / self.processed_count if self.processed_count > 0 else 0.0

    def get_avg_service_time(self):
        return self.sum_service_time / self.processed_count if self.processed_count > 0 else 0.0

    def get_var_waiting_time(self):
        if self.processed_count < 2: return 0.0
        mean = self.get_avg_waiting_time()
        return (self.sum_sq_waiting_time / (self.processed_count - 1)) - (mean ** 2 * self.processed_count / (self.processed_count - 1))

    def get_var_service_time(self):
        if self.processed_count < 2: return 0.0
        mean = self.get_avg_service_time()
        return (self.sum_sq_service_time / (self.processed_count - 1)) - (mean ** 2 * self.processed_count / (self.processed_count - 1))