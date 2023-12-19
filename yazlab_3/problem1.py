import threading
import time
import random
import queue
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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
        'waiter',  # Channel group name
        {
            'type': 'send_status',  # Corresponds to the send_status method in the consumer
            'message': {
                'id': waiter_id,
                'status': status
            }
        }
    )

def manage_tables():
    while True:
        priority, arrival_time, customer_id, customer_event = table_queue.get()
        table_semaphore.acquire()  # Acquire a table
        status = "Priority customer" if priority == 0 else "Customer"
        print(f"{status} {customer_id} has been seated at a table.")
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

        status = "Priority customer" if priority == 0 else "Customer"
        print(f"{status} {customer_id} is waiting for Chef {chef_id}.")
        time.sleep(3)
        print(f"{status} {customer_id}'s order is ready by Chef {chef_id}.")
        chef_queue.task_done()

        customer_event.set()
        customer_event.clear()
        chef_semaphore.release()

def waiter(waiter_id):
    while True:
        waiter_semaphore.acquire()
        try:
            priority, arrival_time, customer_id, customer_event = waiter_queue.get(timeout=1)
        except queue.Empty:
            waiter_semaphore.release()
            continue

        status = "Priority customer" if priority == 0 else "Customer"
        print(f"{status} {customer_id} is waiting for Waiter {waiter_id}.")
        time.sleep(2)
        print(f"{status} {customer_id} has given an order to Waiter {waiter_id}.")
        waiter_queue.task_done()

        chef_queue.put((priority, arrival_time, customer_id, customer_event))

        customer_event.wait()
        customer_event.clear()
        waiter_semaphore.release()

def manage_cash_registers():
    while True:
        priority, arrival_time, customer_id, customer_event = cash_register_queue.get()
        status = "Priority customer" if priority == 0 else "Customer"
        print(f"{status} {customer_id} is paying.")
        time.sleep(1)
        customer_event.set()  # Signal the customer that the cash register is available
        cash_register_queue.task_done()


def customer_process(customer_id):
    is_priority = random.random() < 0.2
    priority = 0 if is_priority else 1
    customer_event = threading.Event()
    eating_event = threading.Event()
    payment_event = threading.Event()

    status = "Priority customer" if priority == 0 else "Customer"

    # Attempt to request a table with a timeout of 20 seconds
    if not table_semaphore.acquire(timeout=20):
        print(f"{status} {customer_id} left the restaurant after waiting too long for a table.")
        return  # Exit the customer process if no table is available within 20 seconds

    # If a table is acquired, proceed with the dining process
    print(f"{status} {customer_id} has been seated at a table.")
    # Request a waiter
    waiter_queue.put((priority, customer_id, customer_id, eating_event))
    eating_event.wait()  # Wait for the waiter to take the order and the chef to prepare the food
    eating_event.clear()

    # Eating
    print(f"{status} {customer_id} is eating.")
    time.sleep(3)  # Simulate the time taken to eat the meal

    # Release the table semaphore to indicate the table is now free
    table_semaphore.release()

    # Request to pay
    cash_register_queue.put((priority, customer_id, customer_id, payment_event))
    payment_event.wait()  # Wait for the cash register to be available
    payment_event.clear()

    print(f"{status} {customer_id} has completed dining and payment.")


# Start threads for managing resources
threading.Thread(target=manage_tables, daemon=True).start()
for chef_id in range(1, chef_count + 1):
    threading.Thread(target=chef, args=(chef_id,), daemon=True).start()

# Start threads for waiters and assign them IDs
for waiter_id in range(1, waiter_count + 1):
    threading.Thread(target=waiter, args=(waiter_id,), daemon=True).start()

threading.Thread(target=manage_cash_registers, daemon=True).start()


# Create customers
for i in range(100):
    if i % 10 == 0:
        time.sleep(5)  # Simulate arrival intervals
    threading.Thread(target=customer_process, args=(i,), daemon=True).start()
    time.sleep(0.1)
