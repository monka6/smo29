class PostDispatcher:
    def __init__(self, buffer):
        self.buffer = buffer
        self.rejected_count = 0

    def accept_log(self, log):
        if self.buffer.has_free_slot():
            self.buffer.put_log(log)
            return True, None
        else:
            evicted = self.buffer.remove_oldest()
            self.rejected_count += 1
            self.buffer.put_log(log)
            return False, evicted

class PickDispatcher:
    def __init__(self, buffer, handlers):
        self.buffer = buffer
        self.handlers = handlers
        self.handler_pointer = 0  

    def find_free_handler(self):
        for _ in range(len(self.handlers)):
            handler = self.handlers[self.handler_pointer]
            if handler.is_free():
                self.handler_pointer = (self.handler_pointer + 1) % len(self.handlers)
                return handler
            self.handler_pointer = (self.handler_pointer + 1) % len(self.handlers)
        return None