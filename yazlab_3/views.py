from django.http.response import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .simulation import start_simulation,waiter_count,chef_count,table_count # This should be the path to your simulation start function
import json
import logging

logger = logging.getLogger(__name__)
def index(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def start_simulation_view(request):
    try:
        # Load customer data from the request body
        # customer_list = json.loads(request.body.decode('utf-8'))
        customer_list = json.loads(request.body)
        start_simulation(customer_list)
        return JsonResponse({'status': 'Simulation started'})
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'Invalid data', 'error': str(e)}, status=400)

def tables_view(request):
    # Render your customers page
    tables = [{'id': i} for i in range(1, table_count + 1)]
    return render(request, 'tables.html', {'tables': tables})

def waiters_view(request):
    # Render your waiters page
    waiters = [{'id': i} for i in range(1, waiter_count + 1)]
    return render(request, 'waiters.html', {'waiters': waiters})

def chefs_view(request):
    # Render your chefs page
    chefs = [{'id': i} for i in range(1, chef_count + 1)]
    return render(request, 'chefs.html', {'chefs': chefs})
