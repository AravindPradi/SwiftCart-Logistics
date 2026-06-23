from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category

def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    query = request.GET.get('q')
    category_slug = request.GET.get('category')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    if category_slug:
        products = products.filter(category__slug=category_slug)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'query': query,
    }
    return render(request, 'products/product_list.html', context)

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'products/product_detail.html', {'product': product})
