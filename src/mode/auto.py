import sys
import os
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mode.model import Model

def print_statistics_tables(model):
    print("\n" + "="*110)
    print("ТАБЛИЦА 1: ХАРАКТЕРИСТИКИ ИСТОЧНИКОВ ВС")
    print("="*110)
    print(f"{'№ Ист.':<8} | {'Кол-во заявок':<14} | {'P_отк':<8} | {'T_преб':<8} | {'T_БП':<8} | {'T_обсл':<8} | {'Д_БП':<8} | {'Д_обсл':<8}")
    print("-" * 110)
    for s in model.sources:
        n = s.get_generated_count()
        p_otk = s.get_prob_reject()
        t_preb = s.get_avg_time_in_system()
        t_bp = s.get_avg_waiting_time()
        t_obsl = s.get_avg_service_time()
        d_bp = s.get_var_waiting_time()
        d_obsl = s.get_var_service_time()
        
        print(f"И{s.id:<7} | {n:<14} | {p_otk:<8.3f} | {t_preb:<8.3f} | {t_bp:<8.3f} | {t_obsl:<8.3f} | {d_bp:<8.3f} | {d_obsl:<8.3f}")

    print("\n" + "="*80)
    print("ТАБЛИЦА 2: ХАРАКТЕРИСТИКИ ПРИБОРОВ (ПЗ1)")
    print("="*80)
    print(f"{'Прибор':<8} | {'Обработано':<12} | {'K_исп':<8} | {'Сум. время занятости':<20}")
    print("-" * 80)
    for h in model.handlers:
        processed = h.get_processed_count()
        k_util = h.get_busy_time() / model.current_time if model.current_time > 0 else 0.0
        print(f"П{h.id:<7} | {processed:<12} | {k_util:<8.3f} | {h.get_busy_time():<20.3f}")
    print("="*80 + "\n")

def run_simulation(num_handlers, buffer_capacity=5, num_steps=2000, num_runs=20):
    sum_time = 0
    sum_reject_prob = 0
    sum_utilization = 0

    lambda_val = 0.8 
    mu_val = 0.5      

    last_model = None

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
        
        last_model = model
        
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

    if last_model:
        total_gen = sum(s.get_generated_count() for s in last_model.sources)
        total_rej = sum(s.get_rejected_count() for s in last_model.sources)
        total_proc = last_model.total_processed
        global_p_rej = total_rej / total_gen if total_gen > 0 else 0.0
        
        sum_lambda = sum(s.lambda_val for s in last_model.sources)
        sum_mu = sum(h.mu_val for h in last_model.handlers)
        rho = sum_lambda / sum_mu if sum_mu > 0 else 0.0
        
        print("\n" + "="*80)
        print("МОДЕЛИРОВАНИЕ ЗАВЕРШЕНО")
        print(f"Время моделирования: {last_model.current_time:.3f} | Шагов: {num_steps}")
        print(f"Заявок: создано {total_gen}; обслужено {total_proc}; отказано {total_rej}; P_отк = {global_p_rej*100:.2f}%")
        print(f"Оценка входной нагрузки rho = Lambda/Mu = {rho:.3f}")
        print("Дисперсии выборочные (деление на n-1), при n<2 отображается 0.")
        print("="*80 + "\n")
        
        print_statistics_tables(last_model)

        return (sum_time / num_runs, 
            sum_reject_prob / num_runs, 
            sum_utilization / num_runs)


if __name__ == "__main__":
    print("АВТОМАТИЧЕСКИЙ РЕЖИМ")
    
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
    plt.title('Зависимость среднего времени пребывания (T_сист) от числа приборов')
    plt.xlabel('Количество приборов (шт.)')
    plt.ylabel('T_сист (среднее)')
    plt.grid(True)
    plt.savefig(f"{output_dir}/graph_time.png", dpi=300, bbox_inches='tight')
    plt.show()

    plt.figure(figsize=(8, 5))
    plt.plot(handlers_range, rejects, marker='s', color='r', linestyle='-')
    plt.title('Зависимость вероятности отказа (P_отк) от числа приборов')
    plt.xlabel('Количество приборов (шт.)')
    plt.ylabel('P_отк')
    plt.grid(True)
    plt.savefig(f"{output_dir}/graph_reject.png", dpi=300, bbox_inches='tight')
    plt.show()

    plt.figure(figsize=(8, 5))
    plt.plot(handlers_range, utils, marker='^', color='g', linestyle='-')
    plt.title('Зависимость коэффициента использования (K_исп) от числа приборов')
    plt.xlabel('Количество приборов (шт.)')
    plt.ylabel('K_исп')
    plt.grid(True)
    plt.savefig(f"{output_dir}/graph_utilization.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Готово! Графики сохранены в папке", output_dir)