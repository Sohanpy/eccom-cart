import os
import random
from django.conf import settings
from django.db.models import Sum
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.db import models

from .utils import unique_slug_generator

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name , ext = os.path.splitext(base_name)
    return name , ext

def upload_image_path(instance, filename):
    new_filename = random.randint(1,45391020459312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "products/{new_filename}/{final_filename}".format(
            new_filename=new_filename, 
            final_filename=final_filename
            )

CATEGORY_CHOICES = (
    ('S' , 'Shirt'),
    ('SW' , 'Sport Wear'),
    ('OW' , 'OutWear'),
)

LABEL_CHOICES = (
    ('P' , 'primary'),
    ('s' , 'secondary'),
    ('d' , 'danger'),
)
class Item(models.Model):
    title = models.CharField(max_length = 20)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True , null=True)
    category = models.CharField(choices = CATEGORY_CHOICES , max_length = 2)
    label = models.CharField(choices = LABEL_CHOICES , max_length = 1)
    slug = models.SlugField(blank = True , unique = True)
    desc = models.TextField()
    image = models.ImageField(upload_to = upload_image_path , null = True , blank = True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('core:detail' , kwargs={
            'slug' : self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })
        

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })
        


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete = models.CASCADE)
    ordered = models.BooleanField()
    item = models.ForeignKey(Item  , on_delete = models.CASCADE)
    quantity = models.IntegerField(default = 1)


    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        return self.quantity * self.item.price
    
    def get_discount_total_item_price(self):
        return self.quantity * self.item.discount_price
    
    def amount_saved(self):
        return self.get_total_item_price() - self.get_discount_total_item_price()

    def final_price(self):
        if self.item.discount_price:
            return self.get_discount_total_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete = models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add= True)
    ordered_date = models.DateTimeField()
    recieved = models.BooleanField(default=False)
    name = models.CharField(max_length = 20)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.final_price()
        return total


def unique_slug_genaretor_reciever(instance , sender , *args , **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
pre_save.connect(unique_slug_genaretor_reciever , sender=Item)