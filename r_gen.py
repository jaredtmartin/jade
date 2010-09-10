from decimal import *
import random
from jade.inventory.models import *
from datetime import datetime
VOWELS=['a','e','i','o','u']
CONSONANTS=['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z']
LETTERS=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
def value(maximum=100):
    return random.randrange(maximum*100)/Decimal('100.00')  
def word():
    l=random.randrange(5)
    word=''
    for x in range(random.randrange(5)+1):
        word+=obj(CONSONANTS)+obj(VOWELS)
    return word
def letter():
    return LETTERS[random.randrange(26)]
def name():
    return word().title()
def phone_number():
    return str(random.randrange(1000, 9999))+"-"+str(random.randrange(1000, 9999))
def obj(objects):
    return objects[random.randrange(len(objects))]
def gen():
    print "Creating 3000 products"
    products(3000)
    print "Creating 300 clients"
    clients(300)
    print "Creating 300 vendors"
    vendors(300)
    print "Creating 1000 purchases"
    purchases(1000)
    print "Creating 800 sales"
    sales(800)
    print "All Done."

def clients(num):
    price_groups=PriceGroup.objects.all()
    tax_groups=TaxGroup.objects.all()
    for client in range(num):
        Client(
            name=name()+' '+name(),
            tax_group=obj(tax_groups),
            price_group=obj(price_groups),
            address =       name(),
            state_name =         name(),
            country =       name(),
            home_phone =    phone_number(),
            cell_phone =    phone_number(),
            work_phone =    phone_number(),
            fax =           phone_number(),
            tax_number =    value(100000),
            description =   word(),
            email =         word()+"@"+word()+'.com',
            registration =  value(100000),
            user =          obj(User.objects.all()),
        ).save()
def vendors(num):
    for vendor in range(num):
        Vendor(name=name()+' '+name()).save()
def sales(num):
    clients=Client.objects.all()
    items=Item.objects.all()
    for doc in range(num):
        client=obj(clients)
        for line in range(random.randrange(5)):
            Sale(
                doc_number='000'+str(doc),
                price=value(),
                cost=value(),
                date=datetime.now(),
                client=client,
                item=obj(items),
                tax=value(),
                discount=value(),
                quantity=value(),
                serial=str(random.randrange(9999999999)),                
            ).save()
def purchases(num):
    vendors=Vendor.objects.all()
    items=Item.objects.all()
    for doc in range(num):
        vendor=obj(vendors)
        for line in range(random.randrange(5)):
            Purchase(
                doc_number='0'+str(doc),
                cost=value(),
                vendor=vendor,
                item=obj(items),
                quantity=value(),
                serial=str(random.randrange(9999999999)),                
            ).save()
def products(num):
    units=Unit.objects.all()
    for x in range(num):
        Item(
            name=name(),
            cost=value(),
            bar_code=str(random.randrange(9999999999)), 
            minimum=value(),
            maximum=value(),
            unit=obj(units),
            location=letter().upper()+str(random.randrange(89)+10)+letter().upper()+str(random.randrange(89)+10)
        ).save()
