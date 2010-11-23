from django import template
from inventory import models
from decimal import *
from django.utils.translation import ugettext_lazy as _
register = template.Library()

@register.simple_tag
def show(x, y):
    if x==y: return ''
    else: return ' style="display:none;" '
    
@register.simple_tag
def price(item, user):
    return "%.2f" % item.price(user)

@register.simple_tag
def tax(doc, tax_name):
    return "%.2f" % doc.tax[tax_name]

@register.filter(name='neg')
def neg(value):
    "Negates the value"
    return value * -1
neg.is_safe = True

@register.simple_tag
def labels(trans):
    from jade.inventory.models import Count
    result=""
    t=trans.subclass
    if type(t)==Count: 
        if t.count: quantity=t.count
        else: quantity=t.item.stock
    else: quantity=t.quantity
#    for x in range(quantity):
##        result += '<div class="barcode" >%s<br><img class="image" src="%s"></div>'% (trans.subclass.item.name, trans.subclass.item.barcode_url())
#        result +='<pdf:barcode value="%s"></pdf:barcode> '%trans.subclass.item.bar_code 
    return ('<div class="barcode">%s<pdf:barcode type="ean13" value="%s"></pdf:barcode></div> '%(t.item.name, t.item.bar_code)) * int(quantity)
#    return result

@register.simple_tag
def barcode(code):
    from jade.inventory.code39 import code39
    return code39(code)
    
def is_sale_or_purchase(obj):
    "Returns true if the object passed is a Sale or Purchase"
    return obj.tipo=='Sale' or obj.tipo=='Purchase'

@register.filter(name='is_positive')
def is_positive(obj):
    "Returns true if the number passed is positive"
    print "obj = " + str(obj)
    print "obj>0 = " + str(obj>0)
    return obj>0
is_positive.is_safe = True

@register.filter(name='is_negative')
def is_negative(obj):
    "Returns true if the number passed is negative"
    print "obj = " + str(obj)
    print "obj<0 = " + str(obj>0)
    return obj>0
is_positive.is_safe = True

@register.filter(name='price')
def price(item, client):
    "returns the price of the item for the client"
    return item.price(client)
price.is_safe = True

@register.filter(name='mult')
def mult(value, arg):
    "Multiplies the value by the multiplier"
    return Decimal(str(value)) * Decimal(str(arg))
mult.is_safe = True

@register.filter(name='div')
def div(value, arg):
    "Divides the value by the arg"
    return Decimal(str(value)) / Decimal(str(arg))
div.is_safe = True

@register.filter(name='plus')
def plus(value, arg):
    "Adds the arg to the value"
    return value + arg
plus.is_safe = True

@register.filter(name='minus')
def minus(value, arg):
    "subtracts the arg from the value"
    return value - arg
minus.is_safe = True

@register.simple_tag
def link(obj, label=None):
    if not obj: return ''
    elif not label: label=obj.__unicode__()
    if label=='': label='None'
    return '<a href="%s" class="action">%s</a><br>' % (obj.url(), label)
    
@register.simple_tag
def transaction(obj):
    print "obj=" + str(obj)
    if not obj: return ''
    return '/inventory/%s.html' % (obj.tipo.lower(),)
    
@register.simple_tag
def debug(obj):
    print "obj=" + str(obj)
    return str(obj)
    
@register.simple_tag
def errors(error_list):
    s=''
    for k,v in error_list.items():
        for error in v:
            if type(error)== unicode: s+='<li class="error message">%s: %s</li>' % (k.title(), error, )
            else: s+='<li class="error message">%s: %s</li>' % (k.title(), error.__unicode__(), )
    return s
    
mult.is_safe = True
@register.simple_tag
def elink(obj, model, pk, attr, clase):
    if not obj: return '<span id="id_%s-%i-%s" value="" class="link %s">None</span><br>' % (model, pk, attr, clase)
    label=obj.__unicode__()
    value=label
    if label=='': label='None'
    url=obj.url()
    return '<a id="id_%s-%i-%s" value="%s" class="link %s" href="%s">%s</a><br>' % (model, pk, attr, value, clase, url, label)

    
@register.simple_tag
def serial_link(obj):
    if (not obj.serial) or (obj.serial==''): return ''
    return '<a href="/inventory/serial/%s/" class="action">%s</a><br>' % (obj.serial, obj.serial)
      
@register.simple_tag
def pages(page, q=''):
    page_num=page.number
    p=page.paginator
    if p.num_pages==1: return ""
    links='<p class="paginator">'
    if page_num>5:
        links += u'<a href="?page=1&q=%s">%s</a>...' % (q,_( 'First'))
    start=max(page_num-4,1)
    end=min(page_num+4,p.num_pages)
    for x in range(start,end+1):
        if x!=start: links+='  '
        if page_num==x: links += u'<span class="this-page">%i</span>' % (x,)
        elif x==end: links += u'<a class="end" href="?page=%i&q=%s">%i</a>' % (x, q, x)
        else: links += u'<a href="?page=%i&q=%s">%i</a>' % (x, q, x)
        
    if page_num < p.num_pages-4:
        links += u'...<a href="?page=%i&q=%s">%s</a>' % (p.num_pages, q,_('Last'))
    links+=' (%i pages)</p>'% (p.num_pages,)
    return links
@register.filter(name='money2word')
#def money2word(n):
#    dollars=int2word(n)
#    cents=int2word((n*100)%100)
#    response=''
#    if abs(n)>=1: 
#        response+=int2word(n) + unicode(_(' dollars '))
#        if (n%1)!=0: response += unicode(_(' and '))
#    if (n%1)!=0: response += int2word((n*100)%100) +unicode( _(' cents '))
#    return response
def money2word(n):
    response=words(n)+unicode(_('dollars '))
    cents=(n*100)%100
    response+= unicode(_('with ')) + unicode(int(cents))+u'/100 ' + unicode(_('cents.'))
    return response
money2word.is_safe = True

@register.filter(name='trunc')
def trunc(s, l=50):
    r=s
    if len(s)> l:
        r=r[0:l-3]+'...'
    return r
trunc.is_safe = True

@register.simple_tag
def total_value(l):
    total=0
    for obj in l: total+=obj.value
    return "$%.2f" % total
        
       
       
       
# integer number to english word conversion
# can be used for numbers as large as 999 vigintillion
# (vigintillion --> 10 to the power 60)
# tested with Python24 vegaseat 07dec2006
@register.filter(name='int2word')
def int2word(n):
    """
    convert an integer number n into a string of english words
    """
    n=int(n)
    # break the number into groups of 3 digits using slicing
    # each group representing hundred, thousand, million, billion, ...
    n3 = []
    r1 = ""
    # create numeric string
    ns = str(n)
    for k in range(3, 33, 3):
        r = ns[-k:]
        q = len(ns) - k
        # break if end of ns has been reached
        if q < -2:
            break
        else:
            if q >= 0:
                n3.append(int(r[:3]))
            elif q >= -1:
                n3.append(int(r[:2]))
            elif q >= -2:
                n3.append(int(r[:1]))
        r1 = r
 
    #print n3 # test
     
    # break each group of 3 digits into
    # ones, tens/twenties, hundreds
    # and form a string
    nw = ""
    for i, x in enumerate(n3):
        b1 = x % 10
        b2 = (x % 100)//10
        b3 = (x % 1000)//100
        #print b1, b2, b3 # test
        if x == 0:
            continue # skip
        else:
            t = unicode(thousands[i])
        if b2 == 0:
            nw = unicode(ones[b1]) + t + nw
        elif b2 == 1:
            nw = unicode(tens[b1]) + t + nw
        elif b2 > 1:
            nw = unicode(twenties[b2]) + unicode(ones[b1]) + t + nw
        if b3 > 0:
            nw = unicode(ones[b3]) + unicode(_("hundred ")) + nw
    return nw

int2word.is_safe = True
############# globals ################
#ones = ["", "one ","two ","three ","four ", "five ","six ","seven ","eight ","nine "]
#tens = ["ten ","eleven ","twelve ","thirteen ", "fourteen ","fifteen ","sixteen ","seventeen ","eighteen ","nineteen "]
#twenties = ["","","twenty ","thirty ","forty ","fifty ","sixty ","seventy ","eighty ","ninety "]
#thousands = ["","thousand ","million ", "billion ", "trillion ","quadrillion ", "quintillion ", "sextillion ", "septillion ","octillion ","nonillion ", "decillion ", "undecillion ", "duodecillion ", "tredecillion ","quattuordecillion ", "sexdecillion ", "septendecillion ", "octodecillion ","novemdecillion ", "vigintillion "]
ones = ["", _("one "), _("two "), _("three "), _("four "), _("five "), _("six "), _("seven "), _("eight "), _("nine ")]
tens = [_("ten "), _("eleven "), _("twelve "), _("thirteen "), _("fourteen "), _("fifteen "), _("sixteen "), _("seventeen "), _("eighteen "), _("nineteen ")]
twenties = ["", "", _("twenty "), _("thirty "), _("forty "), _("fifty "), _("sixty "), _("seventy "), _("eighty "), _("ninety ")]
thousands = ["", _("thousand "), _("million "), _("billion "), _("trillion "), _("quadrillion "), _("quintillion "), _("sextillion "), _("septillion "), _("octillion "), _("nonillion "), _("decillion "), _("undecillion "), _("duodecillion "), _("tredecillion "), _("quattuordecillion "), _("sexdecillion "), _("septendecillion "), _("octodecillion "), _("novemdecillion "), _("vigintillion ")]



from django.utils.translation import ugettext_lazy as _

def thousands(i):
    return [words(int(i/1000))+ unicode(_('thousand ')), i-int(i/1000)*1000]
NUMBERS=[
[1000,thousands],
[900,_('nine hundred ')],
[800,_('eight hundred ')],
[700,_('seven hundred ')],
[600,_('six hundred ')],
[500,_('five hundred ')],
[400,_('four hundred ')],
[300,_('three hundred ')],
[200,_('two hundred ')],
[100,_('one hundred ')],
[90,_('ninety ')],
[80,_('eighty ')],
[70,_('seventy ')],
[60,_('sixty ')],
[50,_('fifty ')],
[40,_('fourty ')],
[30,_('thirty ')],
[20,_('twenty ')],
[19,_('ninteen ')],
[18,_('eighteen ')],
[17,_('seventeen ')],
[16,_('sixteen ')],
[15,_('fifteen ')],
[14,_('fourteen ')],
[13,_('thirteen ')],
[12,_('twelve ')],
[11,_('eleven ')],
[10,_('ten ')],
[9,_('nine ')],
[8,_('eight ')],
[7,_('seven ')],
[6,_('six ')],
[5,_('five ')],
[4,_('four ')],
[3,_('three ')],
[2,_('two ')],
[1,_('one ')],
]

def words(num):
    s=''
    for i in NUMBERS:
        if num >= i[0]:
            if hasattr(i[1],'_proxy____args'):
                s+=unicode(i[1])
                num-=i[0]
            else: 
                a=i[1](num)
                s+=a[0]
                num=a[1]
    return s            
