class Storage:
    def __init__(self):
        self.logs = []
        self.saved_count = 0

    def save_log(self, log):
        self.logs.append(log)
        self.saved_count += 1

    def get_saved_count(self):
        return self.saved_count
    
    def get_logs_count(self):
        return len(self.logs)
    
    def clear(self):
        self.logs.clear()
        self.saved_count = 0