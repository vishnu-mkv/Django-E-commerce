# specific to this view
from cmath import log
from datetime import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView 
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from store.forms import CartEntryForm, ProductForm

from .models import Cart, CartEntry, Product

class ProductListView(ListView):

    model = Product
    template_name = 'list.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_queryset(self):
        if self.request.user.is_staff:
            qs = Product.objects.all()
        else:
            qs = Product.objects.filter(expiry_date__gte=datetime.now())
        
        # return a field inCart to each product
        if self.request.user.is_authenticated:
            for product in qs:
                product.inCart = False
                try:
                    cart = Cart.objects.get(user=self.request.user)
                    for entry in cart.entries.all():
                        if product.id == entry.product.id:
                            product.inCart = True
                            break
                except Cart.DoesNotExist:
                    pass
        
        return qs

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        products = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(products, self.paginate_by)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context['products'] = products
        return context

@method_decorator(staff_member_required, name='dispatch')
class ProductCreateView(CreateView):
    model = Product 
    template_name = 'create.html'
    success_url = reverse_lazy('store:home')
    form_class = ProductForm

@method_decorator(staff_member_required, name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'delete.html'
    success_url = reverse_lazy('store:home')

class ProductDetailView(DetailView):

    model = Product
    template_name = 'detail.html'
    context_object_name = 'product'

@method_decorator(staff_member_required, name='dispatch')
class ProductUpdateView(UpdateView):

    model = Product
    template_name = 'update.html'
    context_object_name = 'product'
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy('store:product-detail', kwargs={'pk': self.object.id})


@require_POST
@csrf_exempt
def cart_add(request):
    data = json.loads(request.body)

# check user logged in
    if not request.user.is_authenticated:
        # redirect to login page
        return JsonResponse({'error': 'You must be logged in to add to cart', 'redirect': reverse_lazy('users:login')})

    cart = Cart.objects.get(user=request.user)
    form = CartEntryForm(data)
    if form.is_valid():
        cd = form.cleaned_data
        cart.addEntry(product_id=cd['product_id'], quantity=cd['quantity'])
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})

# cart view
@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'cart.html', {'cart': cart})

# cart delete
@require_POST
@login_required
@csrf_exempt
def cart_remove(request):
    try:
        data = json.loads(request.body)
        cart = Cart.objects.get(user=request.user)
        product_id = data['product_id']
        product = CartEntry.objects.filter(product_id=product_id, users=request.user)
        cart.entries.remove(*product)
        cart.save()
        print(product)
        for entry in product:
            print(entry.product.name)
            if entry.cart_set.count() == 0:
                entry.delete()
        return JsonResponse({'success': True})
    except e:
        return JsonResponse({'success': False, 'errors': e})