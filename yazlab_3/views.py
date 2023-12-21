from django.http.response import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .simulation import start_simulation,waiter_count,chef_count,table_count, cash_register_count
from .optimization import calculate_best_setup
import json
import logging

logger = logging.getLogger(__name__)
def index(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def start_simulation_view(request):
    try:
        customer_list = json.loads(request.body)
        start_simulation(customer_list,5)
        return JsonResponse({'status': 'Simulation started'})
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'Invalid data', 'error': str(e)}, status=400)
@csrf_exempt  
@require_http_methods(["POST"])
def start_simulation_normal_view(request):
    try:
        data = json.loads(request.body)
        customer_list = data.get('customerList')
        total_time = int(data.get('totalTime'))
        customer_interval = int(data.get('customerInterval'))
        intervals = int(data.get('intervals'))
        customer_count = int(sum(int(item['total']) for item in customer_list)/intervals)
        logger.debug(f"Customer Count : {customer_count}  Customer interval: {customer_interval} total time: {total_time}")
        best_setup,best_profit = calculate_best_setup(total_time,customer_interval,customer_count)
        logger.debug(f"Best setup : {best_setup}  Best profit: {best_profit}")
        return JsonResponse({
    'status': 'Simulation started',
    'best_setup': best_setup,
    'best_profit': best_profit
})
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'Invalid data', 'error': str(e)}, status=400)
    
def cashRegister_view(request):
    cashRegisters = [{'id': i} for i in range(1, cash_register_count + 1)]
    return render(request, 'cash_register.html', {'cashRegisters': cashRegisters})

def tables_view(request):
    tables = [{'id': i} for i in range(1, table_count + 1)]
    return render(request, 'tables.html', {'tables': tables})

def waiters_view(request):
    waiters = [{'id': i} for i in range(1, waiter_count + 1)]
    return render(request, 'waiters.html', {'waiters': waiters})

def chefs_view(request):
    chefs = [{'id': i} for i in range(1, chef_count + 1)]
    return render(request, 'chefs.html', {'chefs': chefs})
