from django.shortcuts import render
import json
from django.utils import timezone
from .models import *
from django.db.models import Sum
from django.db import connection

from django.http import JsonResponse

from decimal import Decimal

# =========================
# HOME - PÁGINA INICIAL
# =========================
def home(request):
    return render(request, 'home.html')
