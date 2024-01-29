# Restaurant Simulation Project

This Django project simulates restaurant operations, managing customers, waiters, and chefs through a multi-threading approach. 

## Problem 1 - Restaurant Simulation

### Description

Problem 1 simulates a restaurant environment where customers arrive and interact with waiters and chefs. Customers can be either priority or regular. Waiters take orders and chefs prepare them. The simulation uses threading to manage multiple customers simultaneously.

### Features
- Multithreaded simulation of a restaurant environment.
- Priority queue implementation to manage customers based on priority status.
- Semaphore synchronization to manage the availability of resources.
- Real-time updates on the status of waiters and chefs via WebSockets.

### Setup

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Run redis server:

    ```bash
    redis-server
    ```

3. Run the server:

    ```bash
    uvicorn yazlab_3.asgi:application --port 8000
    ```

### Usage

Navigate to `http://127.0.0.1:8000/` in your browser to access the simulation interface. Click on the "Start Problem 1 Simulation" button to begin. Use the provided fields to add customers and their priority status.

## Problem 2 - Advanced Restaurant Simulation (Hypothetical)

### Description

Problem 2 estimates the best setup for this restaurant to achieve highest profit possible. This is a hypothetical problem to showcase how the simulation might be extended in the future.

## Used Technologies

### WebSockets
The project uses Django Channels and WebSockets to provide real-time updates to the user interface. Make sure you have Redis server running as it's used as a channel layer backend.
