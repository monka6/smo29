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


def find_required_n(num_handlers,
                    num_sources=2,
                    initial_n=500,
                    max_n=200000,
                    buffer_capacity=5,
                    num_runs=20):
    lambda_val = 0.8
    mu_val = 0.5

    current_n = initial_n
    prev_p = None

    print("=" * 70)
    print(f"ПОИСК N: источников={num_sources}, приборов={num_handlers}, "
          f"буфер={buffer_capacity}, Lambda={num_sources * lambda_val:.2f}, "
          f"Mu={num_handlers * mu_val:.2f}")
    print("=" * 70)

    while True:
        sum_rej = 0
        sum_gen = 0

        for _ in range(num_runs):
            model = Model(
                buffer_capacity=buffer_capacity,
                sources_params=[lambda_val] * num_sources,
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

        print(f"  N = {current_n:>6} событий | P_отк = {p_current:.4f} ({p_current*100:.2f}%)")

        if prev_p is not None:
            diff = abs(p_current - prev_p)
            threshold = 0.1 * p_current
            print(f"  Разница = {diff:.4f} | порог 10% = {threshold:.4f}")

            if diff < threshold:
                print(f"\nТОЧНОСТЬ ДОСТИГНУТА: N = {current_n}, P_отк = {p_current:.4f}\n")
                return p_current, current_n

        prev_p = p_current
        current_n *= 2

        if current_n > max_n:
            print(f"\nДОСТИГНУТ ЛИМИТ: N = {max_n}, P_отк = {p_current:.4f}\n")
            return p_current, current_n


def run_final_simulation(num_handlers, num_events, num_sources=2, buffer_capacity=5):
    lambda_val = 0.8
    mu_val = 0.5

    model = Model(
        buffer_capacity=buffer_capacity,
        sources_params=[lambda_val] * num_sources,
        handlers_params=[mu_val] * num_handlers,
        verbose=False
    )

    processed_events = 0
    for _ in range(num_events):
        if not model.step():
            break
        processed_events += 1

    print("=" * 80)
    print("ФИНАЛЬНОЕ МОДЕЛИРОВАНИЕ ЗАВЕРШЕНО")
    print(f"Конфигурация: источников={num_sources}, приборов={num_handlers}, буфер={buffer_capacity}")
    print(f"Время моделирования: {model.current_time:.3f} | Событий обработано: {processed_events}")

    total_gen = sum(s.get_generated_count() for s in model.sources)
    total_rej = sum(s.get_rejected_count() for s in model.sources)
    total_proc = model.total_processed
    global_p_rej = total_rej / total_gen if total_gen > 0 else 0.0

    sum_lambda = sum(s.lambda_val for s in model.sources)
    sum_mu = sum(h.mu_val for h in model.handlers)
    rho = sum_lambda / sum_mu if sum_mu > 0 else 0.0

    in_buffer = model.buffer.occupied_count
    on_handlers = sum(1 for h in model.handlers if h.is_busy)

    print(f"Событий: генераций {total_gen}, завершений обслуживания {total_proc}")
    print(f"Заявок: создано {total_gen}; обслужено {total_proc}; отказано {total_rej}")
    print(f"       осталось в системе: {in_buffer + on_handlers} "
          f"(в буфере {in_buffer}, на приборах {on_handlers})")
    print(f"Оценка входной нагрузки rho = Lambda/(m*Mu) = {rho:.3f}")
    print("=" * 80 + "\n")

    print_statistics_tables(model)

    avg_time = model.total_time_in_system / total_proc if total_proc > 0 else 0.0
    total_busy = sum(h.get_busy_time() for h in model.handlers)
    utilization = total_busy / (num_handlers * model.current_time) if model.current_time > 0 else 0.0

    print(f"Среднее время пребывания заявки в системе: {avg_time:.3f}")
    print(f"Средний коэффициент использования приборов: {utilization:.3f}\n")

    return avg_time, global_p_rej, utilization


if __name__ == "__main__":
    print("=" * 70)
    print("АВТОМАТИЧЕСКИЙ РЕЖИМ")
    print("=" * 70)


    num_sources = 2       
    num_handlers = 3      
    buffer_capacity = 5   

    print(f"\nКонфигурация: источников={num_sources}, приборов={num_handlers}, "
          f"буфер={buffer_capacity}")
    print(f"Lambda = {num_sources * 0.8:.2f}, Mu = {num_handlers * 0.5:.2f}, "
          f"rho = {num_sources * 0.8 / (num_handlers * 0.5):.3f}\n")

    p_final, n_final = find_required_n(
        num_handlers=num_handlers,
        num_sources=num_sources,
        buffer_capacity=buffer_capacity,
    )

    print("=" * 70)
    print(f"РЕЗУЛЬТАТ ПОИСКА: N = {n_final} событий, P_отк = {p_final:.4f}")
    print("=" * 70 + "\n")

    t, r, u = run_final_simulation(
        num_handlers=num_handlers,
        num_events=n_final,
        num_sources=num_sources,
        buffer_capacity=buffer_capacity,
    )

    