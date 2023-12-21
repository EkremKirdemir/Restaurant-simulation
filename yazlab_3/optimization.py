def calculate_best_setup(total_time, customer_interval, customer_arrival_rate, 
                         table_cost=1, waiter_cost=1, cook_cost=1, customer_earnings=1):
    best_profit = -float('inf')
    best_setup = {'tables': 0, 'waiters': 0, 'chefs': 0}

    num_customer_intervals = total_time // customer_interval
    total_customers = num_customer_intervals * customer_arrival_rate

    time_for_order = 2
    time_to_cook = 3
    time_to_eat = 3
    time_to_pay = 1

    for tables in range(1, total_customers + 1):
        for waiters in range(1, total_customers + 1):
            for chefs in range(1, total_customers + 1):
                service_time_per_customer = time_for_order + time_to_cook + time_to_eat + time_to_pay
                customers_served_per_table = total_time // service_time_per_customer

        
                actual_customers_served = min(
                    tables * customers_served_per_table, 
                    waiters * (total_time // time_for_order), 
                    chefs * (total_time // time_to_cook),
                    total_customers
                )

        
                customers_leaving = max(0, total_customers - actual_customers_served)

        
                actual_customers_served -= customers_leaving

        
                profit = actual_customers_served * customer_earnings - (tables * table_cost + waiters * waiter_cost + chefs * cook_cost)

        
                if profit > best_profit:
                    best_profit = profit
                    best_setup = {'tables': tables, 'waiters': waiters, 'chefs': chefs}

    return best_setup, best_profit


