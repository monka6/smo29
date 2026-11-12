class LogEntry:
    def __init__(self, log_id, source_id, created_at, message="Test log"):
        self.id = log_id
        self.source_id = source_id
        self.created_at = created_at
        self.message = message
        self.start_processing_at = None
        self.end_processing_at = None

    def set_start_processing(self, t):
        self.start_processing_at = t

    def set_end_processing(self, t):
        self.end_processing_at = t

    def get_waiting_time(self):
        if self.start_processing_at is not None:
            return self.start_processing_at - self.created_at
        return 0.0

    def get_processing_time(self):
        if self.start_processing_at is not None and self.end_processing_at is not None:
            return self.end_processing_at - self.start_processing_at
        return 0.0

    def __repr__(self):
        return f"Log{self.id}(Src{self.source_id})"