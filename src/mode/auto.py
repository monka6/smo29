import sys
import os
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mode.model import Model

def run_simulation(num_handlers, buffer_capacity=5, num_steps=2000, num_runs=20):
    
    sum_time = 0
    sum_reject_prob = 0
    sum_utilization = 0

    lambda_val = 0.8 
    mu_val = 0.5      

    for _ in range(num_runs):
        model = Model(
            buffer_capacity=buffer_capacity,
            sources_params=[lambda_val, lambda_val],
            handlers_params=[mu_val] * num_handlers,
            verbose=False 
        )
        
        for _ in range(num_steps):
            if not model.step():
                break
        
        if model.total_processed > 0:
            sum_time += model.total_time_in_system / model.total_processed
        
        total_gen = sum(s.get_generated_count() for s in model.sources)
        total_rej = sum(s.get_rejected_count() for s in model.sources)
        if total_gen > 0:
            sum_reject_prob += total_rej / total_gen
            
        total_busy = 0
        for h in model.handlers:
            busy = h.get_busy_time() 
            if h.is_busy:
                busy += (model.current_time - h.current_log.start_processing_at)
            total_busy += busy
            
        if model.current_time > 0:
            sum_utilization += total_busy / (num_handlers * model.current_time)

    return (sum_time / num_runs, 
            sum_reject_prob / num_runs, 
            sum_utilization / num_runs)


if __name__ == "__main__":
    print("=== АВТОМАТИЧЕСКИЙ РЕЖИМ (ОР2) ===")
    
    while True:
        try:
            min_h = int(input("Введите минимальное количество приборов (например, 1): "))
            max_h = int(input("Введите максимальное количество приборов (например, 5): "))
            
            if min_h < 1:
                print("Ошибка: минимальное количество приборов должно быть >= 1.")
                continue
            if max_h < min_h:
                print("Ошибка: максимальное значение должно быть >= минимального.")
                continue
                
            break 
        except ValueError:
            print("Ошибка: пожалуйста, вводите целые числа.")

    handlers_range = list(range(min_h, max_h + 1))
    
    times = []
    rejects = []
    utils = []

    print(f"\nЗапуск автоматического режима для конфигураций: {handlers_range}...")
    for n in handlers_range:
        print(f"  Тестирование конфигурации с {n} приборами...")
        t, r, u = run_simulation(num_handlers=n)
        times.append(t)
        rejects.append(r)
        utils.append(u)

    print("\nПостроение графиков...")
    
    output_dir = "mode/graphs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.figure(figsize=(8, 5))
    plt.plot(handlers_range, times, marker='o', color='b', linestyle='-')
    plt.title('Зависимость среднего времени пребывания в системе от числа приборов')
    plt.xlabel('Количество приборов (шт.)')
    plt.ylabel('Среднее время в системе')
    plt.grid(True)
    plt.savefig(f"{output_dir}/graph_time.png", dpi=300, bbox_inches='tight')
    plt.show()

    plt.figure(figsize=(8, 5))
    plt.plot(handlers_range, rejects, marker='s', color='r', linestyle='-')
    plt.title('Зависимость вероятности отказа от числа приборов')
    plt.xlabel('Количество приборов (шт.)')
    plt.ylabel('Вероятность отказа')
    plt.grid(True)
    plt.savefig(f"{output_dir}/graph_reject.png", dpi=300, bbox_inches='tight')
    plt.show()

    plt.figure(figsize=(8, 5))
    plt.plot(handlers_range, utils, marker='^', color='g', linestyle='-')
    plt.title('Зависимость коэффициента использования приборов от их количества')
    plt.xlabel('Количество приборов (шт.)')
    plt.ylabel('Коэффициент использования')
    plt.grid(True)
    plt.savefig(f"{output_dir}/graph_utilization.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Готово! Графики сохранены в папке", output_dir)