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

def find_required_n(num_handlers, initial_n=500, max_n=200000, buffer_capacity=5, num_runs=20):
    lambda_val = 0.8
    mu_val = 0.5
    
    current_n = initial_n
    prev_p = None
    
    print(f"\n--- Поиск требуемого N для {num_handlers} приборов (старт с N={initial_n}) ---")
    
    while True:
        sum_rej = 0
        sum_gen = 0
        
        for _ in range(num_runs):
            model = Model(
                buffer_capacity=buffer_capacity,
                sources_params=[lambda_val, lambda_val],
                handlers_params=[mu_val] * num_handlers,
                verbose=False
            )
            for _ in range(current_n):
                if not model.step():
                    break
            
            total_gen = sum(s.get_generated_count() for s in model.sources)
            total_rej = sum(s.get_rejected_count() for s in model.sources)
            sum_gen += total_gen
            sum_rej += total_rej
        
        p_current = sum_rej / sum_gen if sum_gen > 0 else 0.0
        
        print(f"  N = {current_n:>6} P_отк = {p_current:.4f} ({p_current*100:.2f}%)")
        
        if prev_p is not None:
            diff = abs(p_current - prev_p)
            threshold = 0.1 * p_current
            print(f"  Разница = {diff:.4f} (порог 10% от p_current = {threshold:.4f})")
            
            if diff < threshold:
                print(f"Точность достигнута на N = {current_n}\n")
                return p_current, current_n
        
        prev_p = p_current
        current_n *= 2
        
        if current_n > max_n:
            print(f"Достигнут лимит N = {max_n}. Останавливаемся.\n")
            return p_current, current_n

def run_final_simulation(num_handlers, num_steps, buffer_capacity=5):
    lambda_val = 0.8
    mu_val = 0.5
    
    model = Model(
        buffer_capacity=buffer_capacity,
        sources_params=[lambda_val, lambda_val],
        handlers_params=[mu_val] * num_handlers,
        verbose=False 
    )
    
    for _ in range(num_steps):
        if not model.step():
            break
            
    print("\n" + "="*80)
    print("ФИНАЛЬНОЕ МОДЕЛИРОВАНИЕ ЗАВЕРШЕНО")
    print(f"Время моделирования: {model.current_time:.3f} | Шагов: {num_steps}")
    
    total_gen = sum(s.get_generated_count() for s in model.sources)
    total_rej = sum(s.get_rejected_count() for s in model.sources)
    total_proc = model.total_processed
    global_p_rej = total_rej / total_gen if total_gen > 0 else 0.0
    
    sum_lambda = sum(s.lambda_val for s in model.sources)
    sum_mu = sum(h.mu_val for h in model.handlers)
    rho = sum_lambda / sum_mu if sum_mu > 0 else 0.0
    
    print(f"Заявок: создано {total_gen}; обслужено {total_proc}; отказано {total_rej}")
    print(f"Оценка входной нагрузки rho = Lambda/Mu = {rho:.3f}")
    print("="*80 + "\n")
    
    print_statistics_tables(model)
    
    avg_time = model.total_time_in_system / total_proc if total_proc > 0 else 0.0
    total_busy = sum(h.get_busy_time() for h in model.handlers)
    utilization = total_busy / (num_handlers * model.current_time) if model.current_time > 0 else 0.0
    
    return avg_time, global_p_rej, utilization

if __name__ == "__main__":
    print("АВТОМАТИЧЕСКИЙ РЕЖИМ")
    
    num_handlers = 3
    print(f"Тестирование конфигурации с {num_handlers} приборами...\n")
    
    p_final, n_final = find_required_n(num_handlers=num_handlers)
    
    t, r, u = run_final_simulation(num_handlers=num_handlers, num_steps=n_final)
    
    