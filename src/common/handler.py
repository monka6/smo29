import random

class Handler:
    def __init__(self, handler_id, mu_val, storage):
        self.id = handler_id
        self.mu_val = mu_val
        self.storage = storage
        self.is_busy = False
        self.current_log = None
        self.finish_time = 0.0
        
        self.processed_count = 0
        self.busy_time = 0.0
        
        self.sum_service_time = 0.0
        self.sum_sq_service_time = 0.0
        self.sum_waiting_time = 0.0
        self.sum_sq_waiting_time = 0.0

    def is_free(self):
        return not self.is_busy

    def start_processing(self, log, current_time):
        self.is_busy = True
        self.current_log = log
        log.set_start_processing(current_time)
        
        service_time = random.expovariate(self.mu_val)
        self.finish_time = current_time + service_time
        return self.finish_time

    def finish_processing(self):
        log = self.current_log
        if log:
            log.set_end_processing(self.finish_time)
            
            service_time = self.finish_time - log.start_processing_at
            waiting_time = log.get_waiting_time()
            
            self.processed_count += 1
            self.busy_time += service_time
            
            # Суммируем для расчета средних и дисперсий
            self.sum_service_time += service_time
            self.sum_sq_service_time += service_time ** 2
            self.sum_waiting_time += waiting_time
            self.sum_sq_waiting_time += waiting_time ** 2
            
            self.save_to_storage(log)
            
        self.is_busy = False
        self.current_log = None
        return log

    def save_to_storage(self, log):
        self.storage.save_log(log)

    def get_processed_count(self):
        return self.processed_count

    def get_busy_time(self):
        return self.busy_time

    def get_current_log(self):
        return self.current_log

    def get_avg_service_time(self):
        return self.sum_service_time / self.processed_count if self.processed_count > 0 else 0.0

    def get_variance_service_time(self):
        if self.processed_count < 2: return 0.0
        mean = self.get_avg_service_time()
        return (self.sum_sq_service_time / self.processed_count) - (mean ** 2)

    def get_avg_waiting_time(self):
        return self.sum_waiting_time / self.processed_count if self.processed_count > 0 else 0.0

    def get_variance_waiting_time(self):
        if self.processed_count < 2: return 0.0
        mean = self.get_avg_waiting_time()
        return (self.sum_sq_waiting_time / self.processed_count) - (mean ** 2)

    def get_state_str(self):
        return f"H{self.id}(зан.до {self.finish_time:.2f})" if self.is_busy else f"H{self.id}(своб)"