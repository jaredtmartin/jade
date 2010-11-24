# Jade Inventory Control System
#Copyright (C) 2010  Jared T. Martin

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied account of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.test import TestCase
from jade.inventory.models import *
from jade.inventory.forms import *

class TestUpdateSaleForm(TestCase):
    def setUp(self):
        self.client=Account.objects.create(name="Fred", tipo="Client")
        self.client2=Account.objects.create(name="Bob", tipo="Client")
        Account.objects.create(name="Revenue", tipo="Revenue")
        Account.objects.create(name="Cash", tipo="Cash")
        Account.objects.create(name="Inventory", tipo="Inventory")
        Account.objects.create(name="Expense", tipo="Expense")
        Account.objects.create(name="Tax", tipo="Tax")
        Account.objects.create(name="Discount", tipo="Discount")
        self.unit = Unit.objects.create(name='Each')
        self.item = Item.objects.create(name="Dog", unit=self.unit)
        self.item = Item.objects.create(name="Cat", unit=self.unit)
    def test_editing_an_existing_object(self):
        """
        >>> from jade.inventory.models import *
        >>> from jade.inventory.forms import *
        >>> s=Sale.objects.all()[0]
        >>> form = UpdateSaleForm({'quantity':'4', 'pk':str(s.pk)})
        >>> form.is_valid()
        True
        >>> form.save()
        >>> s=Sale.objects.get(pk=s.pk).entry_set.all()
        asdasdasd
        """

class TestSales(TestCase):
    def setUp(self):
        self.client=Account.objects.create(name="Fred", tipo="Client")
        self.client2=Account.objects.create(name="Bob", tipo="Client")
        Account.objects.create(name="Revenue", tipo="Revenue")
        Account.objects.create(name="Cash", tipo="Cash")
        Account.objects.create(name="Inventory", tipo="Inventory")
        Account.objects.create(name="Expense", tipo="Expense")
        Account.objects.create(name="Tax", tipo="Tax")
        Account.objects.create(name="Discount", tipo="Discount")
        self.unit = Unit.objects.create(name='Each')
        self.item = Item.objects.create(name="Dog", unit=self.unit)

    def test_test_saving_existing(self):
        """
        >>> print "Trying again"
        """
    def test_sale_with_cost_but_no_item(self):
        """
        >>> c=Client.objects.get(name='Fred')
        >>> s=Sale(doc_number='111', comments='first', price=3, cost=2, client=c)
        >>> s.save()
        >>> s.entry_set.all()
        [<Entry: Revenue($-3.00) Revenue>, <Entry: Fred($3.00) Client>, <Entry: Inventory($-2.00) Inventory>, <Entry: Expense($2.00) Expense>]
        """
    def test_sale_with_no_item(self):
        """
        >>> c=Client.objects.get(name='Fred')
        >>> s=Sale(doc_number='222', comments='second test', price=3, client=c)
        >>> s.save()
        >>> s.entry_set.all()
        [<Entry: Revenue($-3.00) Revenue> ]
        """
    def test_basic_sale(self):
        """
        >>> c=Client.objects.get(name='Fred')
        >>> i=Item.objects.get(name='Dog')
        >>> s=Sale(doc_number='333', comments='third test', price=3, cost=2, client=c, item=i, quantity=2, serial='3333333')
        >>> s.save()
        >>> s.entry_set.all()
        [<Entry: Revenue($-3.00) Revenue>, <Entry: Fred($3.00) Client>, <Entry: Inventory($-2.00) Inventory>, <Entry: Expense($2.00) Expense>]
        """
class TestAccounts(TestCase):
    def test_creating_and_balance(self):
        """
        >>> a=Account.objects.create(name="AccountTest", tipo="Client")
        >>> a.balance
        Decimal('0.00')
        """
