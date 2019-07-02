from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render , get_object_or_404 , redirect
from django.views.generic import ListView , DetailView , View
from django.utils import timezone

from .forms import CheckoutForm
from .models import Item , OrderItem , Order , Address

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
        try:
            order = Order.objects.get(
                user = self.request.user,
                ordered = False
            )
            form = CheckoutForm
            context = {
                'order':order,
                'form' : form
            }
            shipping_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 's',
                default = True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_billing_address':shipping_address_qs[0]} 
                )

            billing_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'b',
                default = True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address':billing_address_qs[0]}
                )
        except ObjectDoesNotExist:
            messages.warning(self.request , "You don't have any active cart" )
            return redirect('/')
        return render(self.request , "checkout.html" , context)
    
    def post(self , *args , **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(
                user = self.request.user,
                ordered = False
            )
            if form.is_valid():
                use_defaut_address = form.cleaned_data.get(
                    'use_default_shipping'
                )
                if use_default_shipping:
                    print('using default shipping address')
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        urdered = False,
                        default = True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request , "No default shipping address available"
                        )
                        return redirect('core:checkout')
                else:
                    print("user entering a new address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address'
                    )
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2'
                    )
                    shipping_country = form.cleaned_data.get(
                        'shipping_country'
                    )
                    shipping_zip = form.cleaned_data.get(
                        'shipping_zip'
                    )

                    if is_valid_form([shipping_address1 , shipping_country , shipping_zip]):
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address1,
                            apartment_address = shipping_address2,
                            country = shipping_country,
                            zip_code = shipping_zip,
                            address_type = 's'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_detault_shipping = form.cleaned_data.get(
                            'set_detault_shipping'
                        )

                        if set_detault_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(
                            self.request, "please fill in the required shipping address info fields"
                        )
                use_defaut_address = form.cleaned_data.get(
                    'use_defaut_address'
                )
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address'
                )

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type  = 'b'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_defaut_address:
                    print('using the default billing address')
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'b',
                        default = True
                    )

                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.save()
                    else:
                        messages.info(
                            self.request , "No default address available"
                        )
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(
                            self.request , "please fill in the required addresses fileds "
                        )
                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 's':
                    return redirect('core:payment' , payment_option = 'stripe')
                elif payment_option == 'p':
                    return redirect('core:payment' , payment_option = 'paypal')
                else:
                    messages.info(
                        self.warning , "Invalid payment option selected"
                    )
        
        except ObjectDoesNotExist:
            messages.warning(self.request , "you dont have an active order")
            return redirect("core:cart")
