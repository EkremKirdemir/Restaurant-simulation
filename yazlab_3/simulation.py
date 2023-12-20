# simulation.py
import threading
import time
import queue
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, filename='simulation.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
channel_layer = get_channel_layer()

table_count = 6
waiter_count = 3
chef_count = 2
cash_register_count = 1

# Semaphores for waiter and chef counts
waiter_semaphore = threading.Semaphore(waiter_count)
chef_semaphore = threading.Semaphore(chef_count)
table_semaphore = threading.Semaphore(table_count)

# Priority queues
table_queue = queue.PriorityQueue()
waiter_queue = queue.PriorityQueue()
chef_queue = queue.PriorityQueue()
cash_register_queue = queue.PriorityQueue()

def update_waiter_status(waiter_id, status):
    async_to_sync(channel_layer.group_send)(
        'waiter_group',  # This must match the group name used in your consumer
        {
            'type': 'waiter_status',  # This must match the method name in your consumer
            'message': {
                'id': waiter_id,
                'status': status
            }
        }
    )
def update_chef_status(chef_id, status):
    async_to_sync(channel_layer.group_send)(
        'chef_group',  # This must match the group name used in your consumer
        {
            'type': 'chef_status',  # This must match the method name in your consumer
            'message': {
                'id': chef_id,
                'status': status
            }
        }
    )
def update_table_status(table_id, status):
    async_to_sync(channel_layer.group_send)(
        'table_group',  # This must match the group name used in your consumer
        {
            'type': 'table_status',  # This must match the method name in your consumer
            'message': {
                'id': table_id,
                'status': status
            }
        }
    )

def manage_tables():
    while True:
        priority, arrival_time, customer_id, customer_event = table_queue.get()
        table_semaphore.acquire()  # Acquire a table
        status = "Priority customer" if priority else "Customer"
        logging.info(f"{status} {customer_id} has been seated at a table.")
        customer_event.set()  # Signal the customer that a table is available
        table_queue.task_done()

def chef(chef_id):
    while True:
        chef_semaphore.acquire()
        try:
            priority, arrival_time, customer_id, customer_event = chef_queue.get(timeout=1)
        except queue.Empty:
            chef_semaphore.release()
            continue

        status = "Priority customer" if priority else "Customer"
        logging.info(f"{status} {customer_id} is waiting for Chef {chef_id}.")
        update_chef_status(chef_id,f"Chef {chef_id} is preparing dishes of {status} {customer_id}.")
        time.sleep(3)
        update_chef_status(chef_id,f"{status} {customer_id}'s dish is ready by Chef {chef_id}.")
        logging.info(f"{status} {customer_id}'s dish is ready by Chef {chef_id}.")
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
        logging.info(f" Waiter {waiter_id} is taking order from {status} {customer_id}.")
        update_waiter_status(waiter_id,f" Waiter {waiter_id} is taking order from {status} {customer_id}.")
        time.sleep(2)
        update_waiter_status(waiter_id,f"Waiter {waiter_id} is carrying order from {status} {customer_id} to chef.")
        logging.info(f"Waiter {waiter_id} is carrying order from {status} {customer_id} to chef.")
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
        logging.info(f"{status} {customer_id} is paying.")
        time.sleep(1)
        customer_event.set()  # Signal the customer that the cash register is available
        cash_register_queue.task_done()


def customer_process(customer_id,priority):
    customer_event = threading.Event()
    eating_event = threading.Event()
    payment_event = threading.Event()

    status = "Priority customer" if priority else "Customer"

    # Attempt to request a table with a timeout of 20 seconds
    if not table_semaphore.acquire(timeout=20):
        logging.info(f"{status} {customer_id} left the restaurant after waiting too long for a table.")
        return  # Exit the customer process if no table is available within 20 seconds

    # If a table is acquired, proceed with the dining process
    logging.info(f"{status} {customer_id} has been seated at a table.")
    # Request a waiter
    waiter_queue.put((priority, customer_id, customer_id, eating_event))
    eating_event.wait()  # Wait for the waiter to take the order and the chef to prepare the food
    eating_event.clear()

    # Eating
    logging.info(f"{status} {customer_id} is eating.")
    time.sleep(3)  # Simulate the time taken to eat the meal

    # Release the table semaphore to indicate the table is now free
    table_semaphore.release()

    # Request to pay
    cash_register_queue.put((priority, customer_id, customer_id, payment_event))
    payment_event.wait()  # Wait for the cash register to be available
    payment_event.clear()

    logging.info(f"{status} {customer_id} has completed dining and payment.")

def start_simulation(customer_list):
    logging.info("Starting simulation.")
    # Start the threads for managing tables, chefs, and cash registers
    threading.Thread(target=manage_tables, daemon=True).start()
    for chef_id in range(1, chef_count + 1):
        threading.Thread(target=chef, args=(chef_id,), daemon=True).start()
    for waiter_id in range(1, waiter_count + 1):
        threading.Thread(target=waiter, args=(waiter_id,), daemon=True).start()
    threading.Thread(target=manage_cash_registers, daemon=True).start()

    # Create the customer processes based on the customer_list data
    customer_id = 0
    for customer in customer_list:
        total_customers = int(customer['total'])
        priority_customers = int(customer['priority'])
       

        # Create priority customer threads
        for _ in range(priority_customers):
            customer_id += 1
            threading.Thread(target=customer_process, args=(customer_id, True), daemon=True).start()
            time.sleep(0.05)  # Delay between thread starts

        # Create normal customer threads
        for _ in range(total_customers - priority_customers):
            customer_id += 1
            threading.Thread(target=customer_process, args=(customer_id, False), daemon=True).start()
            time.sleep(0.05)
        time.sleep(5)