from django.test import TestCase
from jade.transaction.models import *
from decimal import Decimal
class TransactionTest(TestCase):
    fixtures = ['transactions.json']  
    def setUp(self):
        Transaction.objects.all().delete()
        if Client.objects.count()==0:
            get_field(Client, 'receipt').default=Setting.objects.get(name='Default receipt')._value
            self.client=Client.objects.create(name='Client')
            self.fred=Client.objects.create(name='Fred')
            self.vendor=Vendor.objects.create(name='Bob')
            self.frog=Item.objects.get()
            Setting.objects.create(name='Default client', value=self.client)
    def test_next_number(self):
        self.doc1=Document.objects.create()
        self.assertEqual(self.doc1.number, '1001')
        self.doc2=Document.objects.create()
        self.assertEqual(self.doc2.number, '1002')
        self.doc3=Document.objects.create(number='ASD')
        self.assertEqual(self.doc3.number, 'ASD')
        self.doc4=Document.objects.create(number='ASD1')
        self.assertEqual(self.doc4.number, 'ASD1')
        self.doc5=Document.objects.create()
        self.assertEqual(self.doc5.number, 'ASD2')
        self.doc6=Sale.objects.create()
        self.assertEqual(self.doc6.number, '1001')
        self.doc7=Sale.objects.create()
        self.assertEqual(self.doc7.number, '1002')
    def test_item_cost(self):        
        self.assertEqual(self.frog.cost, 0)
    def test_create_sale(self):
        """
        Tests that we can create a sale and have the values saved
        """
        from datetime import datetime
        # Minimal
        self.sale=SaleLine.objects.create()
        self.assertTrue(not self.sale.pk is None)
        self.assertTrue(isinstance(self.sale,SaleLine))
        self.assertEquals(self.sale.debit.pk, self.client.pk) # Should have used the default client
#        
        # Simple SaleLine (no item)
        self.salea=SaleLine.objects.create(number='00203', debit=self.fred, value=Decimal('3.24'), comments='Hello World', date=datetime(2009,11,23))
        self.assertTrue(not self.salea.pk is None)
        self.assertTrue(isinstance(self.salea,SaleLine))
        self.assertEquals(self.salea.debit.pk, self.fred.pk)
        self.assertEquals(self.salea.number,'00203') # will auto-create document
        self.assertEquals(self.salea.value,Decimal('3.24'))
        self.assertEquals(self.salea.comments,'Hello World')
        self.assertEquals(self.salea.description,'Hello World') # when there is no item, takes comment as description
        self.assertEquals(self.salea.date,datetime(2009,11,23))
        
        # Minimal with Item
        price=self.frog.price_set.get(group=1)
        price.fixed=10
        price.save()
        self.saleb=SaleLine.objects.create(item=self.frog)
        self.assertTrue(not self.saleb.pk is None)
        self.assertTrue(isinstance(self.saleb,SaleLine))
        self.assertEquals(self.saleb.value,Decimal('10.00')) # When theres an item and no value, take the price for the client
        self.assertEquals(self.saleb.description,'Frog') # when there is an item, takes items name as description
        self.assertEquals(self.saleb.quantity,1)
        self.assertEquals(self.saleb.cost_transaction.value,0)
        
        # Maximum
        self.salec=SaleLine.objects.create(number='00203', item=self.frog, debit=self.fred, value=Decimal('3.24'), comments='Hello World', date=datetime(2009,11,23))
        self.assertTrue(not self.salec.pk is None)
        self.assertTrue(isinstance(self.salec,SaleLine))
        self.assertEquals(self.salec.debit.pk, self.fred.pk)
        self.assertEquals(self.salec.number,'00203')
        self.assertEquals(self.salec.value,Decimal('3.24'))
        self.assertEquals(self.salec.comments,'Hello World')
        self.assertEquals(self.salec.description,'Frog') # when there is an item, takes items name as description
        self.assertEquals(self.salec.date,datetime(2009,11,23))
        
        # We just sold items, check their quantities
        self.assertEquals(self.frog.stock,-2)
        
        #deactivating should change the cost too.
        self.assertEquals(self.salec.cost_transaction.active,True)
        self.salec.active=False
        self.salec.save()
        self.assertEquals(self.salec.cost_transaction.active,False)
        self.salec.active=True
        self.salec.save()
        self.assertEquals(self.salec.cost_transaction.active,True)
        
        #changing the quantites
        self.salec.quantity=2
        self.salec.save()
        self.assertEquals(self.salec.cost_transaction.quantity,2)
        self.assertEquals(self.frog.stock,-3)
    def test_create_purchase(self):
        """
        Tests that we can create a sale and have the values saved
        """
        from datetime import datetime
        # Minimal
        self.purchase=PurchaseLine.objects.create()
        self.assertTrue(not self.purchase.pk is None)
        self.assertTrue(isinstance(self.purchase,PurchaseLine))
        self.assertEquals(self.purchase.credit.pk, Setting.get('Default vendor').pk) # Should have used the default vendor
        self.assertEquals(self.purchase.debit.pk, Setting.get('Inventory account').pk)
        # Maximum
        self.purchaseb=PurchaseLine.objects.create(item=self.frog, value=Decimal('10.00'), quantity=2, credit=self.vendor)
        self.assertTrue(not self.purchaseb.pk is None)
        self.assertTrue(isinstance(self.purchaseb,PurchaseLine))
        self.assertEquals(self.purchaseb.value,Decimal('10.00'))
        self.assertEquals(self.purchaseb.description,'Frog')
        self.assertEquals(self.purchaseb.quantity,2)
        self.assertEquals(self.purchaseb.credit,self.vendor)
        self.assertEquals(self.frog.stock,2)
        self.assertEquals(self.frog.cost,5)
        self.assertEquals(self.frog.total_cost,10)
        
        # Minimum with item
        self.purchasec=PurchaseLine.objects.create(item=self.frog)
        self.assertTrue(not self.purchasec.pk is None)
        self.assertTrue(isinstance(self.purchasec,PurchaseLine))
        self.assertEquals(self.purchasec.value,Decimal('5.00'))
        self.assertEquals(self.purchasec.description,'Frog')
        self.assertEquals(self.purchasec.quantity,1)
        self.assertEquals(self.frog.stock,3)
        self.assertEquals(self.frog.cost,5)
        self.assertEquals(self.frog.total_cost,15)
        
        
