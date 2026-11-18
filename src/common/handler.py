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
            self.processed_count += 1
            self.busy_time += (self.finish_time - log.start_processing_at)
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

    def get_state_str(self):
        return f"H{self.id}(зан.до {self.finish_time:.2f})" if self.is_busy else f"H{self.id}(своб)"