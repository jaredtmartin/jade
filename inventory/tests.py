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
from django.test.client import Client as TestClient
from jade.inventory.models import *
from jade.inventory.forms import *
from jade.inventory.views import *
class TestPurchases(TestCase):
    fixtures = ['debug_data.json']  
    def setUp(self):
        self.testclient = TestClient()
        response = self.testclient.post('/login/', {'username': 'tester', 'password': 'tester'})
        Purchase.objects.all().delete()
        for x in range(3): Purchase.objects.create()
                
    def testPurchaseList(self):
        response = self.testclient.get('/inventory/purchases/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 3)
    
    def testPurchaseUpdate(self):
        response = self.testclient.post('/inventory/purchase/1/', {
            'account': 'Big Daddy', 
            'date': '12/27/2010',
            'doc_number': 'blah', 
            'item': 'Frog', 
            'quantity': '777', 
            'serial': 'zoomie', 
            'value': '12.34', 
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=Purchase.objects.get(pk=1)        
        self.failUnlessEqual(response.context['objects'][0], p)
        self.failUnlessEqual(p.account.name, 'Big Daddy')
        self.failUnlessEqual(p.doc_number, 'blah')
        self.failUnlessEqual(p.item.name, 'Frog')
        self.failUnlessEqual(p.quantity, Decimal('777'))
        self.failUnlessEqual(p.serial, 'zoomie')
        self.failUnlessEqual(p.value, Decimal('12.34'))
    def testPurchaseNew(self):
        response = self.testclient.post('/inventory/purchase/new/', {
            'vendor': 'Big Daddy', 
            'doc_number': '12345444', 
            'item': 'Frog', 
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.account.name, 'Big Daddy')
        self.failUnlessEqual(p.doc_number, '12345444')
        self.failUnlessEqual(p.item.name, 'Frog')
    def testPurchaseAddPayment(self):
        p=Purchase.objects.get(pk=1)
        p.value=Decimal('12.34')
        p.doc_number='secret'
        p.save()
        p=Purchase.objects.get(pk=2)
        p.value=Decimal('33.13')
        p.doc_number='secret'
        p.save()
        response = self.testclient.post('/inventory/purchase/1/pay/', {})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.value, Decimal('45.47'))
        self.failUnlessEqual(p.account.name, 'No Especificado')
        self.failUnlessEqual(p.doc_number, 'secret')
class TestAjaxViews(TestCase):
    fixtures = ['debug_data.json']  
    def setUp(self):
        self.testclient = TestClient()
        Transaction.objects.all().delete()
        response = self.testclient.post('/login/', {'username': 'tester', 'password': 'tester'})
    def testSerialHistoryList(self):
        Purchase.objects.create(serial='asdf')
        Purchase.objects.create(serial='assdf')
        Sale.objects.create(serial='asdf')
        response = self.testclient.get('/inventory/serial/asdf/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 4)
    def testTransactionEntrys(self):
        s=Sale.objects.create()
        response = self.testclient.get("/inventory/transaction_entry_list/%i/" % s.pk)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 3)
    def testClientList(self):
        Client.objects.create(name='Fred')
        Client.objects.create(name='Frank')
        response = self.testclient.get("/inventory/client_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 3)
        response = self.testclient.get("/inventory/client_list/?q=Fr")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 2)
    def testSiteList(self):
        response = self.testclient.get("/inventory/site_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 1)
    def testUnitList(self):
        Unit.objects.create(name='Box')
        Unit.objects.create(name='Bag')
        Unit.objects.create(name='Crate')
        Unit.objects.create(name='Pallet')
        response = self.testclient.get("/inventory/unit_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 5)
        response = self.testclient.get("/inventory/unit_list/?q=B")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 2)
    def testTaxRateList(self):
        response = self.testclient.get("/inventory/tax_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 4)
    def testUserList(self):
        response = self.testclient.get("/inventory/user_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 1)
        response = self.testclient.get("/inventory/user_list/?q=test")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 1)
    def testVendorList(self):
        response = self.testclient.get("/inventory/vendor_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 2)
        response = self.testclient.get("/inventory/vendor_list/?q=Big")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 1)
    def testPriceGroupList(self):
        response = self.testclient.get("/inventory/price_group_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 2)
        response = self.testclient.get("/inventory/price_group_list/?q=Pub")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 1)
    def testAccountGroupList(self):
        response = self.testclient.get("/inventory/account_group_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 2)
        response = self.testclient.get("/inventory/account_group_list/?q=Con")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 1)
    def testReportList(self):
        response = self.testclient.get("/inventory/report_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 9)
        response = self.testclient.get("/inventory/report_list/?q=Factur")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 2)
    def testAccountList(self):
        response = self.testclient.get("/inventory/account_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 34)
        response = self.testclient.get("/inventory/account_list/?q=Consu")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 7)
    def testItemList(self):
        response = self.testclient.get("/inventory/item_list/")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 2)
        response = self.testclient.get("/inventory/account_list/?q=Fro")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['object_list']), 1)
class TestPDFViews(TestCase):
    fixtures = ['debug_data.json']  
    def setUp(self):
        self.testclient = TestClient()
        Transaction.objects.all().delete()
        response = self.testclient.post('/login/', {'username': 'tester', 'password': 'tester'})
    def testReceipt(self):
        s1=Sale.objects.create(value=123, doc_number='blah')
        s2=Sale.objects.create(value=33, doc_number='blah')
        response = self.testclient.get("/inventory/sale/blah/receipt.pdf")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['doc'].transactions), 2)
        self.failUnlessEqual(response.context['doc'].value, 156)
    def testGaranteeReport(self):
        pass
        # TODO
#        s1=Sale.objects.create(value=123, doc_number='blah', serial='dadad')
#        s2=Sale.objects.create(value=33, doc_number='blah', serial='fagggg')
#        response = self.testclient.get("/inventory/sale/blah/receipt.pdf")
#        self.failUnlessEqual(response.status_code, 200)
#        self.failUnlessEqual(len(response.context['doc'].transactions), 2)
#        self.failUnlessEqual(response.context['doc'].value, 156)
    def testCountSheet(self):
        c1=Count.objects.create(doc_number='counta', item=Item.objects.all()[0])
        print "c1 = " + str(c1)
        c2=Count.objects.create(doc_number='counta', item=Item.objects.all()[0])
        response = self.testclient.get("/inventory/count/counta/sheet.pdf")
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['doc']), 2)
    def testLabels(self):
        p=Purchase.objects.create(doc_number='buy', item=Item.objects.all()[0])
        response = self.testclient.get("/inventory/labels/buy.pdf")
        self.failUnlessEqual(response.status_code, 200)
        # We didn't use Pisa but created the pdf manually, we'll have to trust it was done right

class TestCounts(TestCase):
    fixtures = ['debug_data.json']  
    def setUp(self):
        self.testclient = TestClient()
        response = self.testclient.post('/login/', {'username': 'tester', 'password': 'tester'})
        Transaction.objects.all().delete()
        for x in range(3): Count.objects.create(item=Item.objects.all()[0])
    def testCountList(self):
        response = self.testclient.get('/inventory/counts/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 3)   
    
    def testCountUpdate(self):
        response = self.testclient.post('/inventory/count/1/', {
            'date': '12/27/2010',
            'doc_number': 'blah', 
            'item': 'Frog', 
            'quantity': '777', 
            'serial': 'zoomie', 
            'value': '12.34', 
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=Count.objects.get(pk=1)        
        self.failUnlessEqual(response.context['objects'][0], p)
        self.failUnlessEqual(p.doc_number, 'blah')
        self.failUnlessEqual(p.item.name, 'Frog')
        self.failUnlessEqual(p.count, Decimal('777'))
        self.failUnlessEqual(p.serial, 'zoomie')
        self.failUnlessEqual(p.unit_cost, Decimal('12.34'))
        self.failUnlessEqual(p.quantity, Decimal('0.00'))
    def testCountNew(self):
        response = self.testclient.post('/inventory/count/new/', {
            'doc_number': '12345444', 
            'item': 'Frog', 
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.doc_number, '12345444')
        self.failUnlessEqual(p.item.name, 'Frog')
    def testCountPost(self):
        c=Count.objects.create(item=Item.objects.all()[0], unit_value=2, count=3)
        response = self.testclient.post('/inventory/count/%i/post/' % c.pk, {})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(response.context['objects'][0], Count.objects.get(pk=c.pk))
        self.failUnlessEqual(p.item.name, 'Frog')
        self.failUnlessEqual(p.count, Decimal('3'))
        self.failUnlessEqual(p.unit_cost, Decimal('2'))
        self.failUnlessEqual(p.quantity, Decimal('3'))
        self.failUnlessEqual(p.value, Decimal('6'))
    def testCountPostAsSale(self):
        c=Count.objects.create(item=Item.objects.all()[0], unit_cost=2, count=10)
        c.post()
        c=Count.objects.create(item=Item.objects.all()[0], unit_cost=2, count=3)
        response = self.testclient.post('/inventory/count/%i/post-as-sale/' % c.pk, {})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(response.context['objects'][0], Sale.objects.get(pk=c.pk))
        self.failUnlessEqual(p.item.name, 'Frog')
        self.failUnlessEqual(p.quantity, Decimal('7'))
        self.failUnlessEqual(p.value, Decimal('14'))
class TestAccounts(TestCase):
    fixtures = ['debug_data.json']  
    def setUp(self):
        self.testclient = TestClient()
        response = self.testclient.post('/login/', {'username': 'tester', 'password': 'tester'})
        Transaction.objects.all().delete()
    def testDeleteAccount(self):
        a=Account.objects.create(name='blah')
        response = self.testclient.post('/inventory/account/%i/delete/' % a.pk, {})
        self.assertRedirects(response, '/inventory/accounts/')
        self.failUnlessEqual(len(Account.objects.filter(pk=a.pk)), 0)
    def testClientList(self):
        c=Client.objects.create(name='Fred')
        c=Client.objects.create(name='Tom')
        response = self.testclient.get('/inventory/clients/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 3)
    def testAccountList(self):
        response = self.testclient.get('/inventory/accounts/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 25)
    def testVendorList(self):
        response = self.testclient.get('/inventory/vendors/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 2)
    def testAccountShow(self):
        response = self.testclient.get('/inventory/account/3/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['object'], Account.objects.get(pk=3))
    def testAccountStatement(self):
        response = self.testclient.get('/inventory/account/3/statement.pdf')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['account'], Account.objects.get(pk=3))
    def testClientNew(self):
        response = self.testclient.post('/inventory/client//', {
            "account_group":"Consumidor Final",
            "address":"9",
            "cell_phone":"5",
            "country":"11",
            "credit_days":"30",
            "description":"3",
            "email":"8",
            "fax":"7",
            "home_phone":"4",
            "multiplier":"1",
            "name":"fuzz",
            "number":"0104004",
            "price_group":"Public",
            "receipt":"Factura de Consumidor Final",
            "registration":"2",
            "state_name":"10",
            "tax_number":"1",
            "user":"tester",
            "work_phone":"6",
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.account_group.name, "Consumidor Final")
        self.failUnlessEqual(p.address, '9')
        self.failUnlessEqual(p.cell_phone, '5')
        self.failUnlessEqual(p.country, '11')
        self.failUnlessEqual(p.credit_days, 30)
        self.failUnlessEqual(p.description, '3')
        self.failUnlessEqual(p.email, '8')
        self.failUnlessEqual(p.fax, '7')
        self.failUnlessEqual(p.home_phone, '4')
        self.failUnlessEqual(p.multiplier, 1)
        self.failUnlessEqual(p.name, 'fuzz')
        self.failUnlessEqual(p.number, '0104004')
        self.failUnlessEqual(p.price_group.name, 'Public')
        self.failUnlessEqual(p.receipt.name, 'Factura de Consumidor Final')
        self.failUnlessEqual(p.registration, '2')
        self.failUnlessEqual(p.state_name, '10')
        self.failUnlessEqual(p.tax_number, '1')
        self.failUnlessEqual(p.user.username, 'tester')
        self.failUnlessEqual(p.work_phone, '6')
    def testVendorNew(self):
        response = self.testclient.post('/inventory/vendor//', {
            "account_group":"Consumidor Final",
            "address":"9",
            "cell_phone":"5",
            "country":"11",
            "credit_days":"30",
            "description":"3",
            "email":"8",
            "fax":"7",
            "home_phone":"4",
            "multiplier":"-1",
            "name":"bill",
            "number":"12345",
            "price_group":"Public",
            "receipt":"Factura de Consumidor Final",
            "registration":"2",
            "state_name":"10",
            "tax_number":"1",
            "user":"tester",
            "work_phone":"6",
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.account_group.name, "Consumidor Final")
        self.failUnlessEqual(p.address, '9')
        self.failUnlessEqual(p.cell_phone, '5')
        self.failUnlessEqual(p.country, '11')
        self.failUnlessEqual(p.credit_days, 30)
        self.failUnlessEqual(p.description, '3')
        self.failUnlessEqual(p.email, '8')
        self.failUnlessEqual(p.fax, '7')
        self.failUnlessEqual(p.home_phone, '4')
        self.failUnlessEqual(p.multiplier, -1)
        self.failUnlessEqual(p.name, 'bill')
        self.failUnlessEqual(p.number, '12345')
        self.failUnlessEqual(p.price_group.name, 'Public')
        self.failUnlessEqual(p.receipt.name, 'Factura de Consumidor Final')
        self.failUnlessEqual(p.registration, '2')
        self.failUnlessEqual(p.state_name, '10')
        self.failUnlessEqual(p.tax_number, '1')
        self.failUnlessEqual(p.user.username, 'tester')
        self.failUnlessEqual(p.work_phone, '6')
    def testAccountNew(self):
        response = self.testclient.post('/inventory/account//', {
            "multiplier":"-1",
            "name":"something",
            "number":"12345",
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.multiplier, -1)
        self.failUnlessEqual(p.name, 'something')
        self.failUnlessEqual(p.number, '12345')
class TestItems(TestCase):
    fixtures = ['debug_data.json']  
    def setUp(self):
        self.testclient = TestClient()
        response = self.testclient.post('/login/', {'username': 'tester', 'password': 'tester'})
        Item.objects.all().delete()
        i=Item.objects.create(name='spring', minimum=3)
        i=Item.objects.create(name='sprocket', minimum=-3)
    def testItemList(self):
        response = self.testclient.get('/inventory/items/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 2)
    def testLowStock(self):
        response = self.testclient.get('/inventory/items/low_stock/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 1)
    def testLowStockReport(self):
        response = self.testclient.get('/inventory/items/low_stock.pdf')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['items']), 1)
    def testPriceReport(self):
        response = self.testclient.get('/inventory/items/prices.pdf')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['items']), 2)
    def testInventoryReport(self):
        response = self.testclient.get('/inventory/items/inventory.pdf')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['items']), 2)
    def testItemShow(self):
        i=Item.objects.all()[0]
        response = self.testclient.get('/inventory/item/%i/'%i.pk)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['object'], i)
    def testItemDelete(self):
        i=Item.objects.all()[0]
        response = self.testclient.post('/inventory/item/%i/delete/'%i.pk)
        self.assertRedirects(response, '/inventory/items/')
        self.failUnlessEqual(Item.objects.filter(pk=i.pk).count(), 0)
    # TODO: item_image_upload
    def testItemNew(self):
        response = self.testclient.post('/inventory/item//', {
            "bar_code":"4",
            "default_cost":"2",
            "description":"7",
            "location":"1",
            "maximum":"6",
            "minimum":"5",
            "name":"bloop",
            "unit":"3",
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.bar_code, "4")
        self.failUnlessEqual(p.default_cost, 2)
        self.failUnlessEqual(p.description, '7')
        self.failUnlessEqual(p.location, '1')
        self.failUnlessEqual(p.maximum, 6)
        self.failUnlessEqual(p.minimum, 5)
        self.failUnlessEqual(p.name, 'bloop')
        self.failUnlessEqual(p.unit.name, '3')
    def testItemEdit(self):
        i=Item.objects.get(name='Sprocket')
        response = self.testclient.post('/inventory/item/%i/'%i.pk, {
            "bar_code":"4",
            "default_cost":"2",
            "description":"7",
            "location":"1",
            "maximum":"6",
            "minimum":"5",
            "name":"bloop",
            "unit":"3",
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.bar_code, "4")
        self.failUnlessEqual(p.default_cost, 2)
        self.failUnlessEqual(p.description, '7')
        self.failUnlessEqual(p.location, '1')
        self.failUnlessEqual(p.maximum, 6)
        self.failUnlessEqual(p.minimum, 5)
        self.failUnlessEqual(p.name, 'bloop')
        self.failUnlessEqual(p.unit.name, '3')
    def testServiceNew(self):
        response = self.testclient.post('/inventory/service//', {
            "bar_code":"4",
            "description":"7",
            "location":"1",
            "name":"bloop",
            "unit":"3",
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.bar_code, "4")
        self.failUnlessEqual(p.description, '7')
        self.failUnlessEqual(p.name, 'bloop')
        self.failUnlessEqual(p.unit.name, '3')
    def testServiceList(self):
        Service.objects.create(name='Car Wash')
        Service.objects.create(name='Repair')
        Service.objects.create(name='Whitewall')
        response = self.testclient.get('/inventory/items/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['page'].object_list), 3)
    def testPriceEdit(self):
        i=Item.objects.get(name='Sprocket')
        response = self.testclient.post('/inventory/price/%i/'%i.pk, {
            "relative":"1",
            "fixed":"2",
        })
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['error_list'], {})
        p=response.context['objects'][0]
        self.failUnlessEqual(p.fixed, 2)
        self.failUnlessEqual(p.relative, 1)
    
    
    
