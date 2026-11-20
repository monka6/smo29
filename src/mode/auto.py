import sys
import os

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


def run_final_simulation(num_handlers, num_events, buffer_capacity=5):
    lambda_val = 0.8
    mu_val = 0.5

    model = Model(
        buffer_capacity=buffer_capacity,
        sources_params=[lambda_val, lambda_val],
        handlers_params=[mu_val] * num_handlers,
        verbose=False
    )

    processed_events = 0
    for _ in range(num_events):
        if not model.step():
            break
        processed_events += 1

    print("\n" + "="*80)
    print("ФИНАЛЬНОЕ МОДЕЛИРОВАНИЕ ЗАВЕРШЕНО")
    print(f"Время моделирования: {model.current_time:.3f} | Событий обработано: {processed_events}")

    total_gen = sum(s.get_generated_count() for s in model.sources)
    total_rej = sum(s.get_rejected_count() for s in model.sources)
    total_proc = model.total_processed
    global_p_rej = total_rej / total_gen if total_gen > 0 else 0.0

    sum_lambda = sum(s.lambda_val for s in model.sources)
    sum_mu = sum(h.mu_val for h in model.handlers)
    rho = sum_lambda / sum_mu if sum_mu > 0 else 0.0

    print(f"Событий: генераций {total_gen}, завершений обслуживания {total_proc}")
    print(f"Заявок: создано {total_gen}; обслужено {total_proc}; отказано {total_rej}")
    print(f"Оценка входной нагрузки rho = Lambda/Mu = {rho:.3f}")
    print("="*80 + "\n")

    print_statistics_tables(model)

    avg_time = model.total_time_in_system / total_proc if total_proc > 0 else 0.0
    total_busy = sum(h.get_busy_time() for h in model.handlers)
    utilization = total_busy / (num_handlers * model.current_time) if model.current_time > 0 else 0.0

    print(f"Среднее время пребывания заявки в системе: {avg_time:.3f}")
    print(f"Средний коэффициент использования приборов: {utilization:.3f}\n")

    return avg_time, global_p_rej, utilization


if __name__ == "__main__":
    print("АВТОМАТИЧЕСКИЙ РЕЖИМ")

    num_handlers = 3
    num_events = 1000  

    print(f"Тестирование конфигурации с {num_handlers} приборами...\n")

    t, r, u = run_final_simulation(num_handlers=num_handlers, num_events=num_events)