from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render , get_object_or_404 , redirect
from django.views.generic import ListView , DetailView , View
from django.utils import timezone

from .models import Item , OrderItem , Order

class HomePageView(ListView):
    model = Item
    context_object_name = 'object_list'
    template_name = 'home.html'

class ProductDetailView(DetailView):
    model = Item
    template_name = 'product.html'


class Cart(LoginRequiredMixin , View):
    def get(self , *args , **kwargs):
        try:
            order = Order.objects.get(user = self.request.user , ordered = False)
            context = {
                'object' : order
            }
            return render(self.request , 'cart.html' , context)
        except ObjectDoesNotExist:
            messages.warning(self.request , "You don't have an active cart")
            return redirect('/')



@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:cart")

@login_required
def remove_from_cart(request , slug):
    item = get_object_or_404(Item , slug=slug)
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False
    )
    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug = item.slug).exists():
            order_item = OrderItem.objects.filter(
                item = item,
                user = request.user,
                ordered = False
            )[0]
            order.items.remove(order_item)
            messages.info(request , "This item was removed from the crat")
            return redirect('core:cart')
        else:
            messages.info(request , "This item was not in your crat")
            return redirect('core:cart')
    else:
        messages.info(request , "You don't have an active cart")
        return redirect('core:cart')

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:detail", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:detail", slug=slug)


class CheckoutView(View):
    def get(self , *args , **kwargs):
        return render(self.request , 'checkout.html')



