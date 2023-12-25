
import threading
import time
import queue
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
from datetime import datetime
import os




logging.basicConfig(level=logging.INFO, filename='simulation.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
channel_layer = get_channel_layer()

table_count = 6
waiter_count = 3
chef_count = 2
cash_register_count = 1

customer_table_assignments = {}
customer_status = {}

waiter_semaphore = threading.Semaphore(waiter_count)
chef_semaphore = threading.Semaphore(chef_count)
table_semaphore = threading.Semaphore(table_count)

table_queue = queue.PriorityQueue()
waiter_queue = queue.PriorityQueue()
chef_queue = queue.PriorityQueue()
cash_register_queue = queue.PriorityQueue()

table_assignments = {i: None for i in range(1, table_count + 1)}
table_lock = threading.Lock()
def clear_log_file():
    base_dir = '/Users/kirdemir/Desktop/yazlab_3/yazlab_3'
    log_file = os.path.join(base_dir, "logs.txt")
    with open(log_file, "w") as f:
        pass
def logMessage(message):
    base_dir = '/Users/kirdemir/Desktop/yazlab_3/yazlab_3'
    log_file = os.path.join(base_dir, "logs.txt")
    with open(log_file, "a") as f:
        f.write("{0} -- {1}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M"), message))

def assign_table(customer_id):
    with table_lock:
        for table_id, assigned_customer in table_assignments.items():
            if assigned_customer is None:
                table_assignments[table_id] = customer_id
                logMessage(f"Table {table_id} assigned to Customer {customer_id}.")
                return table_id
    logMessage(f"No available table for Customer {customer_id}.")
    return None



def release_table(table_id):
    with table_lock:
        table_assignments[table_id] = None
        logMessage(f"Table {table_id} released and now available.")
def update_queue_status(action, customer_id,status):
    async_to_sync(channel_layer.group_send)(
        'table_group',
        {
            'type': 'update_queue_status',
            'message': {
                'status': status,
                'action': action,
                'customer_id': customer_id
            }
        }
    )

def update_cashRegister_status(cashRegister_id, status):
    async_to_sync(channel_layer.group_send)(
        'cashRegister_group', 
        {
            'type': 'cashRegister_status', 
            'message': {
                'id': cashRegister_id,
                'status': status
            }
        }
    )
def update_waiter_status(waiter_id, status):
    async_to_sync(channel_layer.group_send)(
        'waiter_group', 
        {
            'type': 'waiter_status', 
            'message': {
                'id': waiter_id,
                'status': status
            }
        }
    )
def update_chef_status(chef_id, status):
    async_to_sync(channel_layer.group_send)(
        'chef_group', 
        {
            'type': 'chef_status', 
            'message': {
                'id': chef_id,
                'status': status
            }
        }
    )
def update_table_status(table_id, status):
    async_to_sync(channel_layer.group_send)(
        'table_group', 
        {
            'type': 'table_status', 
            'message': {
                'id': table_id,
                'status': status
            }
        }
    )



def release_table(table_id):
    with table_lock:
        table_assignments[table_id] = None
        logMessage(f"Table {table_id} released and now available.")
        table_semaphore.release()




def chef(chef_id):
    while True:
        chef_semaphore.acquire()
        try:
            priority, arrival_time, customer_id, customer_event = chef_queue.get(timeout=1)
        except queue.Empty:
            chef_semaphore.release()
            continue

        status = "Priority customer" if priority else "Customer"
    
        update_chef_status(chef_id,f"Chef {chef_id} is preparing dishes of {status} {customer_id}.")
        logMessage(f"Chef {chef_id} is preparing dishes of {status} {customer_id}.")
        time.sleep(3)
        update_chef_status(chef_id,f"{status} {customer_id}'s dish is ready by Chef {chef_id}.")
        logMessage(f"{status} {customer_id}'s dish is ready by Chef {chef_id}.")
        chef_queue.task_done()

        customer_event.set()
        customer_event.clear()
        chef_semaphore.release()
        update_chef_status(chef_id,f"Chef {chef_id} is Idle.")

def waiter(waiter_id):
    while True:
        waiter_semaphore.acquire()
        try:
            priority, arrival_time, customer_id, customer_event = waiter_queue.get(timeout=1)
        except queue.Empty:
            waiter_semaphore.release()
            continue

        status = "Priority customer" if priority else "Customer"
    
        update_waiter_status(waiter_id,f" Waiter {waiter_id} is taking order from {status} {customer_id}.")
        logMessage(f" Waiter {waiter_id} is taking order from {status} {customer_id}.")
        time.sleep(2)
        update_waiter_status(waiter_id,f"Waiter {waiter_id} is carrying order from {status} {customer_id} to chef.")
        logMessage(f"Waiter {waiter_id} is carrying order from {status} {customer_id} to chef.")
    
        waiter_queue.task_done()

        chef_queue.put((priority, arrival_time, customer_id, customer_event))

        customer_event.wait()
        customer_event.clear()
        waiter_semaphore.release()
        update_waiter_status(waiter_id,f"Waiter {waiter_id} is Idle.")


def manage_cash_registers():
    while True:
        priority, arrival_time, customer_id, customer_event = cash_register_queue.get()
        status = "Priority customer" if priority else "Customer"
    
        update_cashRegister_status(1,f"{status} {customer_id} is paying.")
        logMessage(f"{status} {customer_id} is paying.")
        time.sleep(1)
        update_cashRegister_status(1,"Available")
        customer_event.set() 
        cash_register_queue.task_done()
def manage_tables():
    while True:
        priority, arrival_time, customer_id, customer_event = table_queue.get()


        if table_semaphore.acquire(blocking=True, timeout=20):
    
            if customer_status.get(customer_id) == "left":
                logMessage(f"Customer {customer_id} already left, cannot be seated.")
                table_semaphore.release()
                table_queue.task_done()
                continue
            table_id = assign_table(customer_id)
            if table_id is not None:
                customer_table_assignments[customer_id] = table_id
                logMessage(f"Customer {customer_id} seated at table {table_id}.")
                update_table_status(table_id, f"Customer {customer_id} seated.")
                customer_event.set()
            else:
        
                table_semaphore.release()
                logMessage(f"Error: Semaphore acquired but no table was actually free for Customer {customer_id}.")
        else:
    
            logMessage(f"Customer {customer_id} left the restaurant after waiting too long for a table.")
            customer_table_assignments.pop(customer_id, None)

        table_queue.task_done()

def customer_process(customer_id, priority):
    customer_event = threading.Event()
    eating_event = threading.Event()
    payment_event = threading.Event()

    status = "Priority customer" if priority else "Customer"
    update_queue_status('add_to_queue', customer_id, status)
    customer_status[customer_id] = "waiting"

    customer_priority = 0 if priority else 1
    table_queue.put((customer_priority, time.time(), customer_id, customer_event))

    seated = customer_event.wait(timeout=20)
    if not seated:
        logMessage(f"{status} {customer_id} left the restaurant after waiting too long for a table.")
        customer_table_assignments.pop(customer_id, None)
        customer_status[customer_id] = "left"
        update_queue_status('remove_from_queue', customer_id, status)
        update_queue_status('add_to_left', customer_id, status)
        return

    table_id = customer_table_assignments.get(customer_id)
    if table_id is None:
        logMessage(f"Error in table assignment for {status} {customer_id}")
        return

    update_queue_status('remove_from_queue', customer_id, status)
    logMessage(f"{status} {customer_id} has been seated at table {table_id}.")
    update_table_status(table_id, f"{status} {customer_id} is waiting for waiter")
    customer_status[customer_id] = "seated"

    waiter_queue.put((priority, time.time(), customer_id, eating_event))
    eating_event.wait()

    if customer_status[customer_id] == "left":
        return

    logMessage(f"{status} {customer_id} is eating")
    update_table_status(table_id, f"{status} {customer_id} is eating")
    customer_status[customer_id] = "eating"
    time.sleep(3)

    cash_register_queue.put((priority, time.time(), customer_id, payment_event))
    payment_event.wait()

    if customer_status[customer_id] == "left":
        return

    logMessage(f"{status} {customer_id} is paying.")
    update_cashRegister_status(1, f"{status} {customer_id} is paying.")
    customer_status[customer_id] = "paying"
    time.sleep(1)

    release_table(table_id)
    logMessage(f"Table {table_id} released by {status} {customer_id}.")
    update_table_status(table_id, "Available")
    customer_status[customer_id] = "completed"
    customer_table_assignments.pop(customer_id, None)




def start_simulation(customer_list,customer_interval):
    clear_log_file()
    logMessage("Starting simulation.")
    logMessage("Simulation Started")
    time.sleep(5)
    
    threading.Thread(target=manage_tables, daemon=True).start()
    for chef_id in range(1, chef_count + 1):
        threading.Thread(target=chef, args=(chef_id,), daemon=True).start()
    for waiter_id in range(1, waiter_count + 1):
        threading.Thread(target=waiter, args=(waiter_id,), daemon=True).start()
    threading.Thread(target=manage_cash_registers, daemon=True).start()


    customer_id = 0
    for customer in customer_list:
        total_customers = int(customer['total'])
        priority_customers = int(customer['priority'])


    
        for _ in range(priority_customers):
            customer_id += 1
            threading.Thread(target=customer_process, args=(customer_id, True), daemon=True).start()
            time.sleep(0.05) 

    
        for _ in range(total_customers - priority_customers):
            customer_id += 1
            threading.Thread(target=customer_process, args=(customer_id, False), daemon=True).start()
            time.sleep(0.05)
        time.sleep(customer_interval)