from django.http.response import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .simulation import start_simulation  # This should be the path to your simulation start function
import json
import logging

logger = logging.getLogger(__name__)
def index(request):
    logger.debug("sadasd")
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def start_simulation_view(request):
    logger.debug("sadasdasd")
    try:
        # Load customer data from the request body
        # customer_list = json.loads(request.body.decode('utf-8'))
        customer_list = json.loads(request.body)
        start_simulation(customer_list)
        return JsonResponse({'status': 'Simulation started'})
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'Invalid data', 'error': str(e)}, status=400)

def customers_view(request):
    # Render your customers page
    return render(request, 'customers.html')

def waiters_view(request):
    # Render your waiters page
    return render(request, 'waiters.html')

def chefs_view(request):
    # Render your chefs page
    return render(request, 'chefs.html')
