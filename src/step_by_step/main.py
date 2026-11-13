import os
from model import Model

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    model = Model(
        buffer_capacity=3, 
        sources_params=[0.5, 0.3], 
        handlers_params=[0.4, 0.4] 
    )
    
    print("=== СИМУЛЯЦИЯ СЕРВИСА СБОРА ЛОГОВ (ПОШАГОВЫЙ РЕЖИМ) ===")
    print("Нажимайте Enter для перехода к следующему событию (или 'q' для выхода).\n")
    
    step_count = 0
    max_steps = 20 
    
    while step_count < max_steps:
        user_input = input("Нажмите Enter...")
        if user_input.lower() == 'q':
            break
            
        if not model.step():
            print("Больше нет событий.")
            break
            
        step_count += 1

    print("\n=== ИТОГИ МОДЕЛИРОВАНИЯ ===")
    print(f"Всего шагов (событий): {step_count}")
    print(f"Сгенерировано логов: {sum(s.generated_count for s in model.sources)}")
    print(f"Обработано логов: {model.total_processed}")
    print(f"Отказов (потеряно): {model.total_rejected}")
    if model.total_processed > 0:
        avg_wait = model.total_waiting_time / model.total_processed
        print(f"Среднее время ожидания: {avg_wait:.3f} мс")