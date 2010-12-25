from django.db import models
from jade.inventory.models import Item
from django.contrib.sessions.models import Session


class CartItem(models.Model):
    session = models.ForeignKey(Session)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    item = models.ForeignKey(Item, unique=False)
    class Meta:
        db_table = 'cart_items'
        ordering = ['date_added']
    def total(self):
        return self.quantity * self.item.price(Setting.get('Default client'))
    def name(self):
        return self.item.name
    def price(self):
        return self.item.price
    def get_absolute_url(self):
        return self.product.get_absolute_url()
    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()

