import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.buffer import Buffer
from common.source import Source
from common.handler import Handler
from common.dispatchers import PostDispatcher, PickDispatcher
from common.storage import Storage

class Model:
    def __init__(self, buffer_capacity, sources_params, handlers_params):
        self.current_time = 0.0
        self.buffer = Buffer(capacity=buffer_capacity)
        self.storage = Storage()
        self.sources = [Source(i+1, lambda_val=lam) for i, lam in enumerate(sources_params)]
        self.handlers = [Handler(i+1, mu_val=mu, storage=self.storage) for i, mu in enumerate(handlers_params)]
        self.post_dispatcher = PostDispatcher(self.buffer)
        self.pick_dispatcher = PickDispatcher(self.buffer, self.handlers)
        
        for src in self.sources:
            src.next_generation_time = random.expovariate(src.lambda_val)
            
        self.total_processed = 0
        self.total_waiting_time = 0.0

    def get_next_event(self):
        events = []
        for src in self.sources:
            events.append((src.next_generation_time, 'GEN', src))
        for h in self.handlers:
            if h.is_busy:
                events.append((h.finish_time, 'FIN', h))
        
        if not events:
            return None
        events.sort(key=lambda x: x[0])
        return events[0]

    def step(self):
        next_event = self.get_next_event()
        if not next_event:
            return False
            
        time, event_type, obj = next_event
        self.current_time = time
        
        event_text = ""
        action_text = ""

        if event_type == 'GEN':
            log = obj.generate_log(self.current_time)
            event_text = f"Лог от И{obj.id} (t={self.current_time:.2f})"
            
            accepted, evicted = self.post_dispatcher.accept_log(log)
            if accepted:
                action_text = f"Поставлен в буфер (Д1031)"
            else:
                evicted_source = self.sources[evicted.source_id - 1] 
                evicted_source.rejected_count += 1
                action_text = f"БУФЕР ПОЛОН! Вытеснен {evicted} от И{evicted.source_id} (Д10О3)"
                
        elif event_type == 'FIN':
            log = obj.finish_processing()
            event_text = f"Прибор {obj.id} закончил {log} (t={self.current_time:.2f})"
            self.total_processed += 1
            self.total_waiting_time += log.get_waiting_time()
            action_text = f"Обработка завершена"
            
        while self.buffer.has_logs():
            free_handler = self.pick_dispatcher.find_free_handler()
            if not free_handler:
                break 
            picked_log = self.pick_dispatcher.pick_log_from_buffer()  
            free_handler.start_processing(picked_log, self.current_time)
            
            if action_text:
                action_text += f" -> {picked_log} назначен на П{free_handler.id} (Д2Б3, Д2П2)"
            else:
                action_text = f"{picked_log} назначен на П{free_handler.id} (Д2Б3, Д2П2)"

        self.print_event(event_text, action_text)
        return True

    def print_event(self, event_text, action_text):
        print("-" * 60)
        print(f"[t ={self.current_time:>7.3f}] СОБЫТИЕ: {event_text}")
        print(f"          ДЕЙСТВИЕ: {action_text}")
        buffer_str = self.buffer.get_state_str()
        print(f"          БУФЕР: {buffer_str} (занято {self.buffer.occupied_count}/{self.buffer.capacity})")
        print(f"          УКАЗАТЕЛИ: УБ={self.buffer.get_write_pointer()} | УВ={self.buffer.get_read_pointer()} | УП={self.pick_dispatcher.get_handler_pointer()}")
        h_states = " | ".join([h.get_state_str() for h in self.handlers])
        print(f"          ПРИБОРЫ: {h_states}")
        total_rej = sum(s.get_rejected_count() for s in self.sources)
        rejects_str = ", ".join([f"И{s.id}: {s.get_rejected_count()}" for s in self.sources if s.get_rejected_count() > 0])
        print(f"          ОТКАЗОВ: всего {total_rej} ({rejects_str if rejects_str else 'нет'})")
        print(f"          В ХРАНИЛИЩЕ: {self.storage.get_saved_count()} логов")

        if self.total_processed > 0:
            avg_wait = self.total_waiting_time / self.total_processed
            print(f"          СРЕДНЕЕ ВРЕМЯ ОЖИДАНИЯ: {avg_wait:.3f}")
        print()