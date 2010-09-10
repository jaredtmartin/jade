from django.db import models
from jade.inventory.models import Item
from decimal import *

class Combo(models.Model):
    root = models.ForeignKey(Item, unique=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    item = models.ForeignKey(Item)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)

