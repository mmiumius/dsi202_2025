from django.shortcuts import render, get_object_or_404
from .models import Clothing
import random

def welcome(request):
    return render(request, 'clothes/welcome.html')

def home(request):
    query = request.GET.get('q', '')
    if query:
        items = Clothing.objects.filter(name__icontains=query).order_by('-id')
    else:
        all_items = list(Clothing.objects.all())
        items = random.sample(all_items, min(len(all_items), 6))  # สุ่มสูงสุด 6 ชิ้น
    return render(request, 'clothes/home.html', {'items': items, 'query': query})

def detail(request, pk):
    item = get_object_or_404(Clothing, pk=pk)
    return render(request, 'clothes/detail.html', {'item': item})
