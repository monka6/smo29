import os
from model import Model

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    model = Model(
        buffer_capacity=3, 
        sources_params=[2.0, 2.0], 
        handlers_params=[0.5, 0.5] 
    )
    
    print("СИМУЛЯЦИЯ СЕРВИСА СБОРА ЛОГОВ")
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

