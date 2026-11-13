import sys
import os
import random

# Добавляем путь к папке src, чтобы Питон видел папку common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.buffer import Buffer
from common.source import Source
from common.handler import Handler
from common.dispatchers import PostDispatcher, PickDispatcher

class Model:
    def __init__(self, buffer_capacity, sources_params, handlers_params):
        self.current_time = 0.0
        
        # Настройка компонентов
        self.buffer = Buffer(capacity=buffer_capacity)
        self.sources = [Source(i+1, lambda_val=lam) for i, lam in enumerate(sources_params)]
        self.handlers = [Handler(i+1, mu_val=mu) for i, mu in enumerate(handlers_params)]
        
        self.post_dispatcher = PostDispatcher(self.buffer)
        self.pick_dispatcher = PickDispatcher(self.buffer, self.handlers)
        
        # Инициализация первых событий
        for src in self.sources:
            src.next_generation_time = random.expovariate(src.lambda_val)
            
        # Статистика
        self.total_rejected = 0
        self.total_processed = 0
        self.total_waiting_time = 0.0

    def get_next_event(self):
        events = []
        # События от источников
        for src in self.sources:
            events.append((src.next_generation_time, 'GEN', src))
        # События от приборов
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

        # 1. Обработка события
        if event_type == 'GEN':
            log = obj.generate_log(self.current_time)
            event_text = f"Лог от И{obj.id} (t={self.current_time:.2f})"
            
            accepted, evicted = self.post_dispatcher.accept_log(log)
            if accepted:
                action_text = f"Поставлен в буфер (Д1031)"
            else:
                self.total_rejected += 1
                action_text = f"БУФЕР ПОЛОН! Вытеснен {evicted} (Д10О3)"
                
        elif event_type == 'FIN':
            log = obj.finish_processing()
            event_text = f"Прибор {obj.id} закончил {log} (t={self.current_time:.2f})"
            self.total_processed += 1
            self.total_waiting_time += log.get_waiting_time()
            action_text = f"Обработка завершена"
            
        # 2. Триггер выбора из буфера
        while self.buffer.has_logs():
            free_handler = self.pick_dispatcher.find_free_handler()
            if not free_handler:
                break
            picked_log = self.buffer.get_log()
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
        print(f"          УКАЗАТЕЛИ: УБ={self.buffer.write_pointer} | УВ={self.buffer.read_pointer} | УП={self.pick_dispatcher.handler_pointer}")
        h_states = " | ".join([h.get_state_str() for h in self.handlers])
        print(f"          ПРИБОРЫ: {h_states}")
        print(f"          ОТКАЗОВ: {self.total_rejected}")
        print() 