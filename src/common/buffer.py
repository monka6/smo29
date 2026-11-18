class Buffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.slots = [None] * capacity
        self.write_pointer = 0 
        self.read_pointer = 0   
        self.occupied_count = 0

    def has_free_slot(self):
        return self.occupied_count < self.capacity

    def has_logs(self):
        return self.occupied_count > 0

    def put_log(self, log):
        if not self.has_free_slot():
            return False
        
        while self.slots[self.write_pointer] is not None:
            self.write_pointer = (self.write_pointer + 1) % self.capacity
        
        self.slots[self.write_pointer] = log
        self.occupied_count += 1
        self.write_pointer = (self.write_pointer + 1) % self.capacity
        return True

    def find_oldest_slot(self):
        oldest_idx = -1
        oldest_time = float('inf')
        for i, log in enumerate(self.slots):
            if log is not None and log.created_at < oldest_time:
                oldest_time = log.created_at
                oldest_idx = i
        return oldest_idx

    def remove_oldest(self):
        idx = self.find_oldest_slot()
        if idx != -1:
            oldest_log = self.slots[idx]
            self.slots[idx] = None
            self.occupied_count -= 1
            return oldest_log
        return None

    def get_log(self):
        if not self.has_logs():
            return None
        
        while self.slots[self.read_pointer] is None:
            self.read_pointer = (self.read_pointer + 1) % self.capacity
            
        log = self.slots[self.read_pointer]
        self.slots[self.read_pointer] = None
        self.occupied_count -= 1
        self.read_pointer = (self.read_pointer + 1) % self.capacity
        return log

    def get_write_pointer(self):
        return self.write_pointer

    def get_read_pointer(self):
        return self.read_pointer

    def get_state_str(self):
        return "[" + ", ".join(str(s) if s else " _ " for s in self.slots) + "]"