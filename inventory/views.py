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
from jade.inventory.models import Count, Sale, Purchase, Tab
from jade.inventory.forms import *
#from django.template import loader, Context, RequestContext
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import http

from django.contrib.sites.models import Site
import os
from django.db.models import Q
from django.shortcuts import get_object_or_404, render_to_response, HttpResponseRedirect
from django.template.loader import get_template
import ho.pisa as pisa
import cStringIO as StringIO
from django.template import Template, Context, RequestContext
import cgi
from django.views.generic import list_detail
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings

def root(response):
    return HttpResponseRedirect('/inventory/sales/')
    
def set_languages(request):
    request.session['django_language'] = request.GET.get('lang', 'en')
    return http.HttpResponseRedirect(request.META['HTTP_REFERER'])
    
def _paginate(request, queryset):
    paginator = Paginator(queryset, 25, orphans=3)
    try: page_num = int(request.GET.get('page', '1'))
    except ValueError: page_num = 1
    try:page = paginator.page(page_num)
    except (EmptyPage, InvalidPage): page = paginator.page(paginator.num_pages)
    return page

def _r2r(request, template, context={}): 
    return render_to_response(template, context, context_instance=RequestContext(request))

def edit_object(request, object_id, model, form, prefix, tipo=None, extra_context={}):
    # Looks up an object, returning 404 if not found, and either updates the object with form, or returns a form to fill out
    # To: Test: 
    # returns 404 if not found.
    # returns correct form and correct item when GET
    # saves item correctly when POST
    # uses correct form if specified and if not
    # TODO
    # Should work without tipo
    # Should work in different languages
    obj = get_object_or_404(model, pk=object_id)
    if not request.user.has_perm('inventory.change_'+obj.tipo.lower()): return http.HttpResponseRedirect("/blocked/")
    f = form(request.POST, instance=obj)
    if not tipo: tipo=obj.get_tipo_display()
    if f.is_valid():
        obj=f.save()
        updated_form=form(instance=obj, prefix=prefix+'-'+str(obj.pk))
        if type(tipo)!=unicode: tipo=unicode(tipo)
        info_list=['The '+tipo+' has been saved successfully.',]
        error_list={}
    else:
        info_list=[]
        error_list=f.errors
        updated_form=form(instance=obj, prefix=prefix+'-'+str(obj.pk))
    extra_context.update({'objects':[obj],'form':updated_form,'info_list':info_list,'error_list':error_list,'prefix':prefix,'line_template':"inventory/transaction.html",'tipo':tipo})
    return _r2r(request,'inventory/results.html', extra_context)
    
def delete_object(request, object_id, model, prefix, tipo=None):
    # Looks up the object and deletes it if you have permission
    # Test: That it deletes it.
    obj = get_object_or_404(model, pk=object_id)
    if not request.user.has_perm('inventory.delete_'+obj.tipo.lower()): return http.HttpResponseRedirect("/blocked/")
    if not tipo: tipo=obj.get_tipo_display()
    obj.delete()
    info_list=[u'The '+unicode(tipo)+u' has been deleted successfully.',]
    return _r2r(request,'inventory/results.html', {'error_list':{}, 'info_list':info_list})

def new_object(request, form, prefix, template='', tipo=None, extra_context={}):
    if tipo and not request.user.has_perm('inventory.change_'+tipo.lower()): return http.HttpResponseRedirect("/blocked/")
    if request.POST:
        f = form(request.POST)
        if f.is_valid():      
            m=f.save(commit=False)
            if tipo:obj=f.save(tipo=tipo)
            else:obj=f.save()
            updated_form=form(instance=obj, prefix=prefix+'-'+str(obj.pk))
            info_list=['The %s has been created successfully.'% tipo, ]
            error_list={}
            obj.edit_mode=True
        else:
            info_list=[]
            obj=None
            error_list=f.errors
            updated_form=None
        if not tipo: tipo=prefix
        extra_context.update({'objects':[obj],'edit_mode':True, 'form':updated_form,'info_list':info_list,'error_list':error_list,'prefix':tipo,'line_template':"inventory/"+prefix+".html"})
        return _r2r(request,'inventory/results.html', extra_context)
    else:
        form=form(prefix=prefix+'-')
        if not tipo: tipo=prefix
        extra_context.update({'form':form,'prefix':tipo,'tipo':tipo})
        #print "extra_context = " + str(extra_context)
        return _r2r(request,template, extra_context)
    
def search_entries(user, form, tipo=None):
    # Searches entrys based on q, start, and end
    # also filters that they are of type tipo if tipo is given
    # TODO Doesnt check for user permissions
    entries = Entry.objects.all().order_by('-date')
    if tipo: entries=entries.filter(tipo=tipo)
    if not form.cleaned_data['q']=='': entries=entries.filter(transaction__doc_number=form.cleaned_data['q'])
    if form.cleaned_data['start']: entries=entries.filter(date__gte=form.cleaned_data['start'])
    if form.cleaned_data['end']: entries=entries.filter(date__lt=form.cleaned_data['end']+timedelta(days=1))
    return entries

def search_transactions(user, form, transactions, strict=True):
    # searches for transactions based on q, start, and end, and users rights
    if not user.has_perm('inventory.view_sale'):transactions=transactions.exclude(tipo='Sale')
    if not user.has_perm('inventory.view_purchase'):transactions=transactions.exclude(tipo='Purchase')
    if not user.has_perm('inventory.view_count'):transactions=transactions.exclude(tipo='Count')
    if not user.has_perm('inventory.view_process'):transactions=transactions.exclude(tipo='Process')
    if not user.has_perm('inventory.view_production'):transactions=transactions.exclude(tipo='Production')
    if not user.has_perm('inventory.view_productionorder'):transactions=transactions.exclude(tipo='ProductionOrder')
    if not form.cleaned_data['q']=='': 
        if strict: transactions=transactions.filter(doc_number=form.cleaned_data['q'])
        else: transactions=transactions.filter(doc_number__icontains=form.cleaned_data['q'])
    if form.cleaned_data['start']: transactions=transactions.filter(_date__gte=form.cleaned_data['start'])
    if form.cleaned_data['end']: transactions=transactions.filter(_date__lt=form.cleaned_data['end']+timedelta(days=1))
    return transactions
    
def paginate_transactions(request, form, collection, template='inventory/transactions.html', errors=[]):
    # takes a collection of transactions and paginates them
    # TODO This function also creates some sums. This should probably be in a separate function
    page = _paginate(request,collection)
    tax = cost = charge = discount = price = None
    try:q=form.cleaned_data['q']
    except: q=''
    try: start=form.cleaned_data['start']
    except: start=None
    try: end=form.cleaned_data['end']
    except: end=None
    if q!='':
        for t in page.object_list.all():
            s=t.subclass
            try: tax=(tax or 0) + s.tax
            except AttributeError: pass
            try: cost=(cost or 0) + s.cost
            except AttributeError: pass
            try: charge=(charge or 0) + s.charge
            except AttributeError: pass
            try: discount=(discount or 0) + s.discount
            except AttributeError: pass
            try: price=(price or 0) + s.price
            except AttributeError: pass
    return _r2r(request,template, {
        'page':page,
        'prefix':'transaction',
        'q':q,
        'cost':cost,
        'start':start,
        'end':end,
        'tax':tax,
        'discount':discount,
        'price':price,
        'search_by_date':True,
        'charge':charge,
        'show_totals':True,
        'error_list':form.errors,
        })
def search_and_paginate_transactions(request, model, template='inventory/transactions.html', errors={}, strict=True):
    # Searches for transactions and paginates them
    form=SearchForm(request.GET, validate=True)
    q=form.cleaned_data['q']
    start=form.cleaned_data['start']
    end=form.cleaned_data['end']
    if q: transactions=search_transactions(request.user, form, model.objects.all(), strict)
    else: transactions=search_transactions(request.user, form, model.objects.filter(sites__id__exact=settings.SITE_ID), strict)
    for k,v in errors.items(): form.errors[k]=v
    return paginate_transactions(request, form, transactions, template)

######################################################################################
# Purchase Views
######################################################################################
@login_required
@permission_required('inventory.view_purchase', login_url="/blocked/")
def list_purchases(request):
    # returns a paginated list of purchases filtered by 'q', 'start', and 'end'
    return search_and_paginate_transactions(request, Purchase,'inventory/purchases.html')

@login_required
@permission_required('inventory.change_purchase', login_url="/blocked/")
def edit_purchase(request, object_id):
    return edit_object(request, object_id, Purchase, PurchaseForm, "purchase")

@login_required
@permission_required('inventory.change_purchase', login_url="/blocked/")
def new_purchase(request):
    error_list={}
    value=0
    item=None
    try: doc_number=request.POST['doc_number']
    except: doc_number='' 
    if doc_number=='': doc_number=Purchase.objects.next_doc_number()
    try: 
        sample=Purchase.objects.filter(doc_number=doc_number)[0]
        date=sample.date
        vendor=sample.vendor
    except:
        date=datetime.now()
        vendor=Vendor.objects.default()
    vendor=Vendor.objects.get_or_create_by_name(name=request.POST['vendor'])

    try: 
        item=Item.objects.fetch(request.POST['item'])
        value=item.cost
    except Item.MultipleObjectsReturned: 
        error_list['item']=['There are more than one %ss with the name %s. Try using a bar code.' % ('item', request.POST['item'])]
    except Item.DoesNotExist: 
        if request.POST['item']!='': error_list['item']=["Unable to find '%s' in the list of items." % (request.POST['item'], )]
    if not vendor: error_list['vendor']=[unicode('Unable to find a vendor with the name specified.')]
    purchase=Purchase(doc_number=doc_number, date=date, vendor=vendor, item=item, value=value)
    purchase.save()
    purchase.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[purchase],'prefix':'purchase','line_template':"inventory/transaction.html",'error_list':error_list, 'info_list':{}})

@login_required
@permission_required('inventory.change_vendorpayment', login_url="/blocked/")
def add_payment_to_purchase(request, object_id):
    obj = get_object_or_404(Purchase, pk=object_id)
    doc=Transaction.objects.filter(doc_number=obj.doc_number)
    total=0
    for transaction in doc:
        for entry in transaction.entry_set.filter(account=obj.vendor):
            if entry.active: total-=entry.value
    payment=VendorPayment(doc_number=obj.doc_number, date=obj.date, debit=obj.vendor, value=total)
    payment.save()
    payment.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[payment],'prefix':'vendorpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})
  

######################################################################################
#                                      Ajax Views
######################################################################################
@login_required
def serial_history(request, serial):
    return _r2r(request,'inventory/entry_list.html', {'page':_paginate(request, Entry.objects.filter(serial=serial)), 'q':''})

@login_required
def ajax_transaction_entry_list(request, object_id):
    t=Transaction.objects.get(pk=object_id)
    inventory_entry=t.entry('Inventory')
    return _r2r(request,'inventory/transaction_entry_list.html', {'page':_paginate(request, Entry.objects.filter(transaction=object_id)), 'inventory_entry':inventory_entry, 'transaction_id':object_id})
 
@login_required
@permission_required('inventory.view_client', login_url="/blocked/")
def ajax_client_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':Client.objects.filter(name__icontains=q),'q':q})

@login_required
@permission_required('inventory.view_site', login_url="/blocked/")
def ajax_site_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':Site.objects.filter(name__icontains=q),'q':q})

@login_required
@permission_required('inventory.view_unit', login_url="/blocked/")
def ajax_unit_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':Unit.objects.filter(name__icontains=q),'q':q})

@login_required
@permission_required('inventory.view_tax', login_url="/blocked/")
def ajax_tax_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':TaxRate.objects.filter(name__icontains=q),'q':q})
     
@login_required
@permission_required('inventory.view_user', login_url="/blocked/")
def ajax_user_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':User.objects.filter(username__icontains=q),'q':q})

@login_required
@permission_required('inventory.view_vendor', login_url="/blocked/")
def ajax_vendor_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':Vendor.objects.filter(name__icontains=q),'q':q})
@login_required
@permission_required('inventory.view_price_group', login_url="/blocked/")
def ajax_price_group_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':PriceGroup.objects.filter(name__icontains=q),'q':q})
@login_required
def ajax_account_group_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':AccountGroup.objects.filter(name__icontains=q),'q':q})

@login_required
def ajax_report_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':Report.objects.filter(name__icontains=q),'q':q})

@login_required
@permission_required('inventory.view_account', login_url="/blocked/")
def ajax_account_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    accounts=Account.objects.filter(name__icontains=q)
    if not request.user.has_perm('inventory.view_client'):accounts=accounts.exclude(tipo='Client')
    if not request.user.has_perm('inventory.view_vendor'):accounts=accounts.exclude(tipo='Vendor')
    return _r2r(request,'inventory/ajax_list.html', {'object_list':accounts,'q':q})

@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def ajax_item_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':Item.objects.filter(name__icontains=q),'q':q})
######################################################################################
# PDF Functions
######################################################################################
def fetch_resources(uri, rel):
    #path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_ROOT, ""))
    path=uri
    return path
    
def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    from datetime import datetime
    context_dict.update({'company_name':Setting.get('Company name'),'date_#printed':datetime.now()})
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), dest=result, link_callback=fetch_resources)
    if not pdf.err:
        return http.HttpResponse(result.getvalue(), mimetype='application/pdf')
    return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))
    
def render_string_to_pdf(request, template, context_dict):
    context = RequestContext(request, context_dict)
    from datetime import datetime
    context_dict.update({'company_name':Setting.get('Company name'),'date_#printed':datetime.now()})
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), dest=result, link_callback=fetch_resources)
    if not pdf.err:
        return http.HttpResponse(result.getvalue(), mimetype='application/pdf')
    return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))

def fallback_to_transactions(request, doc_number, error):
    request.GET=request.GET.copy()
    request.GET['q']=doc_number
    return transaction_list(request, {'Report':[unicode(error),]})

def render_report(request, name, context={}):
    try:report=Report.objects.get(name=name)
    except Report.DoesNotExist: 
        return account_show(request, context['account'].pk, errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (name,)  ),]})
    return render_string_to_pdf(request, Template(report.body), context)
def doc_inactive(doc):
    for line in doc:
        if line.active or line.delivered: return False
    return True
@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def quote(request, doc_number):
    doc=Document(doc_number)
    if len(doc.lines)==0: return fallback_to_transactions(request, doc_number, _('Unable to find sales with the specified document number.'))
    try:report=Setting.get('Quote report')
    except Report.DoesNotExist: 
        return fallback_to_transactions(request, doc_number, _('Unable to find a report for quotes. Check the system setting called "Quote report".') )
    if 'test' in request.GET:
        return render_string_to_pdf(request, Template(report.body), {'doc':doc, 'watermark_filename':report.watermark_url})
    else:
        return render_string_to_pdf(request, Template(report.body), {'watermark_filename':None, 'doc':doc})

@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def sale_receipt(request, doc_number):
    doc=Document(doc_number)
    if len(doc.lines)==0: return fallback_to_transactions(request, doc_number, _('Unable to find sales with the specified document number.'))
    if doc.inactive(): return quote(request, doc_number)
    report=doc[0].subclass.client.receipt
    #print "report = " + str(report)
    if 'test' in request.GET:
        return render_string_to_pdf(request, Template(report.body), {'doc':doc, 'watermark_filename':report.watermark_url})
    else:
        return render_string_to_pdf(request, Template(report.body), {'watermark_filename':None, 'doc':doc})

@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def garantee_report(request, doc_number):
    doc=ClientGarantee.objects.filter(doc_number=doc_number)
    if doc.count()==0: return fallback_to_transactions(request, doc_number, _('Unable to find sales with the specified document number.'))
    try:report=Setting.get('Garantee report')
    except Report.DoesNotExist: 
        return fallback_to_transactions(request, doc_number, _('Unable to find a report template with the name "%s"') % Setting.get('Garantee report').name)
    return render_string_to_pdf(request, Template(report.body), {'doc':doc})

@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def count_sheet(request, doc_number):
    doc=Count.objects.filter(doc_number=doc_number)
    if doc.count()==0: return fallback_to_transactions(request, doc_number, 'Unable to find counts with the specified document number.')
    try:report=Setting.get('Count sheet report')
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
        request.GET['q']=doc_number
        errors={'Report':[unicode('Unable to find a report template with the name"%s"' % (Setting.get('Count sheet report').name,))]}
        return transaction_list(request, errors=errors)
    total=0
    for t in doc:
        s=t.subclass
        try: total+=s.cost
        except AttributeError: pass
    return render_string_to_pdf(request, Template(report.body), {'watermark_filename':report.watermark_url, 'doc':doc,'total':total})
       
@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def labels(request, doc_number):    
    from reportlab.pdfgen import canvas
    doc=Transaction.objects.filter(doc_number=doc_number).filter(Q(tipo='Count')|Q(tipo='Purchase'))
    if doc.count()==0: return fallback_to_transactions(request, doc_number, _('Unable to find counts or purchases with the specified document number.'))
    labels={}
    x=0
    response = http.HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s.pdf' % doc_number
    p = canvas.Canvas(response)
    for trans in doc:
        t=trans.subclass
        if type(t)==Count: 
            if t.count: quantity=t.count
            else: quantity=t.item.stock
        else: quantity=t.quantity
        filepath = os.path.join(settings.APP_LOCATION+'/'+settings.BARCODES_FOLDER, t.item.bar_code+'.png')
        for label in range(quantity):
            if x>=Setting.get('Lines per page'):
                p.showPage()
                x-=Setting.get('Lines per page')
            p.drawImage(filepath, x%Setting.get('Labels per line')*150, p._pagesize[1]-(x/Setting.get('Labels per line')+1)*75)
            x+=1
    p.showPage()
    p.save()
    return response

######################################################################################
#                                 Count Views
######################################################################################
@login_required
@permission_required('inventory.view_count', login_url="/blocked/")
def list_counts(request):
    try: q=request.GET['q']
    except KeyError: q=''
    if q=='': page=_paginate(request, Count.objects.all().order_by('-_date'))
    else: page=_paginate(request, Count.objects.filter(doc_number=q).order_by('-_date'))
    
    return _r2r(request,'inventory/counts.html', {'page':page,'prefix':'transaction','q':q})

@login_required
@permission_required('inventory.change_count', login_url="/blocked/")
def edit_count(request, object_id):
    return edit_object(request, object_id, Count, CountForm, "count")
    
@login_required
@permission_required('inventory.change_count', login_url="/blocked/")
def new_count(request):
    item=None
    try: doc_number=request.POST['doc_number']
    except: doc_number='' 
    if doc_number=='': doc_number=Count.objects.next_doc_number()
    try: 
        sample=Count.objects.filter(doc_number=doc_number)[0]
        date=sample.date
    except:
        date=datetime.now()
    try:
        item=Item.objects.fetch(request.POST['item'])
    except Item.MultipleObjectsReturned: 
        error_list['item']=['There are more than one %ss with the name %s. Try using a bar code.' % ('item', request.POST['item'])]
    except Item.DoesNotExist: 
        if request.POST['item']!='': error_list['item']=["Unable to find '%s' in the list of items." % (request.POST['item'], )]
    try: unit_cost=abs(item.cost)
    except: unit_cost=0
    count=Count(doc_number=doc_number, date=date, item=item, unit_cost=unit_cost)
    count.save()
    count.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[count],'prefix':'count','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.post_count', login_url="/blocked/")
def post_count(request, object_id):
    count = get_object_or_404(Count, pk=object_id)
    success=count.post()
    if success: info_list=[_('The count has been posted successfully.'),]
    else: info_list=[]
    return _r2r(request,'inventory/results.html', {'objects':[count],'prefix':'count','line_template':"inventory/transaction.html", 'error_list':count.errors, 'info_list':info_list})
@login_required
@permission_required('inventory.post_count_sale', login_url="/blocked/")
def post_count_as_sale(request, object_id):
    result=Count.objects.post_as_sale(object_id)
    if not result.errors: 
        info_list=[_('The count has been posted as a sale successfully.'),]
        return _r2r(request,'inventory/results.html', {
            'objects':[result],
            'prefix':'sale',
            'line_template':"inventory/transaction.html",
            'error_list':{}, 
            'info_list':info_list})
    else: 
        info_list=[]
        return _r2r(request,'inventory/results.html', {'objects':[result],'prefix':'count','line_template':"inventory/transaction.html", 'error_list':result.errors, 'info_list':info_list})
    

######################################################################################
#                                 Accounts Views
######################################################################################
@login_required
@permission_required('inventory.change_item', login_url="/blocked/")
def delete_account(request, object_id):
    account = get_object_or_404(Account, pk=object_id)
    account.delete()
    try: redirect=request.GET['redirect_url']
    except: redirect="/inventory/accounts/"
    return http.HttpResponseRedirect(redirect)
@login_required
@permission_required('inventory.view_client', login_url="/blocked/")
def client_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/client_list.html', {'page':_paginate(request, Client.objects.filter(name__icontains=q)),'q':q})
@login_required
@permission_required('inventory.view_account', login_url="/blocked/")
def account_list(request):
    try: 
        q=request.GET['q']
        n=re.split(':', request.GET['q'])[0]
        try: l=re.split(':', request.GET['q'])[1]
        except IndexError: l=None
    except KeyError: 
        n=q=''
        l=None
    accounts=Account.objects.filter(Q(name__icontains=n)|Q(number__startswith=n))
    if l: accounts=accounts.filter(number__regex="^[0987654321]{1,%s}$" % l)
    if not request.user.has_perm('inventory.view_client'):accounts=accounts.exclude(tipo='Client')
    if not request.user.has_perm('inventory.view_vendor'):accounts=accounts.exclude(tipo='Vendor')
    return _r2r(request,'inventory/all_accounts_list.html', {'page':_paginate(request, accounts),'q':q})

@login_required
@permission_required('inventory.view_vendor', login_url="/blocked/")
def vendor_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/vendor_list.html', {'page':_paginate(request, Vendor.objects.filter(name__icontains=q)),'q':q})

#@login_required
#@permission_required('inventory.view_branch', login_url="/blocked/")
#def branch_list(request):
#    try: q=request.GET['q']
#    except KeyError: q=''
#    return _r2r(request,'inventory/branch_list.html', {'page':_paginate(request, Branch.objects.filter(name__icontains=q)),'q':q})

@login_required
def account_show(request, object_id, errors={}):
    if request.POST:
        obj = get_object_or_404(Account, pk=object_id)
        if obj.tipo=='Account': return edit_object(request, object_id, Account, AccountForm, "account")
        else: return edit_object(request, object_id, Account, ContactForm, "account")
#        return edit_object(request, object_id, Account, ContactForm, "account")
    else:
        account = get_object_or_404(Account, pk=object_id)
        if not request.user.has_perm('inventory.view_client') and account.tipo=="Client": return http.HttpResponseRedirect("/blocked/")
        if not request.user.has_perm('inventory.view_vendor') and account.tipo=="Vendor": return http.HttpResponseRedirect("/blocked/")
        form=ContactForm(instance=account, prefix='account-'+str(account.pk))
                
        return list_detail.object_detail(request,
            queryset = Account.objects.all(),
            object_id=object_id,
            template_name = 'inventory/account_show.html',
            extra_context = {
                'entry_page': _paginate(request, Entry.objects.filter(account__number__startswith=account.number, active=True)),
                'form': form,
                'prefix': 'account',
                'error_list':errors,
                'tipo':account.tipo.lower(),
            }
        )
@login_required
@permission_required('inventory.view_client', login_url="/blocked/")
def account_statement(request, object_id): # GET ONLY
    account = get_object_or_404(Account, pk=object_id)
    entries=list(account.entry_set.all().order_by('date'))
    if not request.user.has_perm('inventory.view_client') and account.tipo=="Client": return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.view_vendor') and account.tipo=="Vendor": return http.HttpResponseRedirect("/blocked/")
    entries=list(Entry.objects.raw("select inventory_entry.id, doc_number, inventory_transaction.tipo, value, sum(value), date from inventory_entry inner join inventory_transaction on transaction_id = inventory_transaction.id where account_id=%i group by inventory_transaction.tipo, date order by date" % account.pk))
    total=0
    for entry in entries:
        total+=entry.value
        entry.total=total
    return render_report(request, Setting.get('Account statement report').name, {'account':account,'entries':entries})
@login_required
@permission_required('inventory.change_client', login_url="/blocked/")
def new_client(request):
    if request.POST:
        if not request.POST['user'] or request.POST['user']=='':
            request.POST=request.POST.copy()
            request.POST['user']=unicode(request.user.username)
    return new_object(request, ClientForm, "account", 'inventory/account_show.html', tipo='Client', extra_context={'tipo':'client'})
@login_required
@permission_required('inventory.change_vendor', login_url="/blocked/")
def new_vendor(request):
    
    return new_object(request, VendorForm, "account", 'inventory/account_show.html', tipo='Vendor', extra_context={'tipo':'vendor'})
@login_required
@permission_required('inventory.change_account', login_url="/blocked/")
def new_account(request):
    return new_object(request, AccountForm, "account", 'inventory/account_show.html', tipo='Account', extra_context={'tipo':'account'})

######################################################################################
#                                   Item Views
######################################################################################
@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def item_list(request, errors=[]):
    try: q=request.GET['q']
    except KeyError: q=''
    items=Item.objects.find(q)
    if items.count()==1: return item_show(request, items[0].pk)
    return _r2r(request,'inventory/item_list.html', {'page':_paginate(request, items),'q':q, 'error_list':errors, 'boxform':BoxForm()})

@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def low_stock(request, errors=[]):
    items=Item.objects.low_stock()
    return _r2r(request,'inventory/low_stock.html', {'page':_paginate(request, items), 'q':'', 'error_list':errors, 'boxform':BoxForm()})

@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def low_stock_report(request):
    items=Item.objects.low_stock()
    count=len(items)
    try:report=Setting.get('Low stock report')
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (Setting.get('Low stock report').name,))]}
        return low_stock(request, errors=errors)
    return render_string_to_pdf(request, Template(report.body), {'items':items, 'user':request.user, 'count':count})  
    
@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def price_report(request):
    try: q=request.GET['q']
    except KeyError: q=''
    items=Item.objects.find(q)
    #print "items = " + str(items)
    try:report=Setting.get('Price report')
    except Report.DoesNotExist:
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (Setting.get('Price report').name,))]}
        return item_list(request, errors=errors)
    return render_string_to_pdf(request, Template(report.body), {'items':items, 'user':request.user})
@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def inventory_report(request):
    try: q=request.GET['q']
    except KeyError: q=''
    items=Item.objects.find(q)
    count=items.count()
    total_cost=0
    total_total_cost=0
    total_stock=0
    for item in items:
        total_cost+=item.cost
        total_total_cost+=item.total_cost
        total_stock+=item.stock
    try:report=Setting.get('Inventory report')
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (Setting.get('Inventory report').name,))]}
        return item_list(request, errors=errors)
    return render_string_to_pdf(request, Template(report.body), {'items':items, 'user':request.user, 'total_cost':total_cost, 'total_total_cost':total_total_cost, 'total_stock':total_stock,'count':count})  
    
    
@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def item_show(request, object_id):
    if request.POST:
        if not request.user.has_perm('inventory.change_item'): return http.HttpResponseRedirect("/blocked/")
        return edit_object(request, object_id, Item, ItemForm, "item")
    else:
        item = get_object_or_404(Item, pk=object_id)
        garantee_forms=[GaranteeOfferForm(instance=garantee, prefix="garanteeoffer-"+str(garantee.pk)) for garantee in item.garanteeoffer_set.all()]
        form=ItemForm(instance=item, prefix='item-'+str(item.pk))
        return list_detail.object_detail(request,
            queryset = Item.objects.all(),
            object_id=object_id,
            template_name = 'inventory/item_show.html',
            extra_context = {
                'entry_page': _paginate(request, Entry.objects.filter(item=item, account=Setting.get('Inventory account'))),
                'form': form,
                'tipo':item.tipo,
                'tabkw':'show_item'
            }
        )
@login_required
@permission_required('inventory.delete_item', login_url="/blocked/")
def delete_item(request, object_id):
    item = get_object_or_404(Item, pk=object_id)
    item.delete()
    return http.HttpResponseRedirect("/inventory/items/")
    
@login_required
@permission_required('inventory.change_item', login_url="/blocked/")
def item_image_upload(request, object_id):
    item = get_object_or_404(Item, pk=object_id)
    form = ItemImageForm(request.POST, request.FILES)
    result=form.is_valid()
    #print "result = " + str(result)
    if result: 
        item.image=form.cleaned_data['image']
        item.save()
    return _r2r(request,'inventory/item_image.html', {'item':item})
        
@login_required
@permission_required('inventory.add_item', login_url="/blocked/")
def new_item(request):
    return new_object(request, ItemForm, "item", 'inventory/item_show.html', tipo='Item')

@login_required
@permission_required('inventory.change_item', login_url="/blocked/")
def edit_item(request, object_id):
    return edit_object(request, object_id, Item, ItemForm, "item")
@login_required
@permission_required('inventory.add_service', login_url="/blocked/")
def new_service(request):
    return new_object(request, ItemForm, "item", 'inventory/item_show.html', tipo='Service')
@login_required
@permission_required('inventory.view_service', login_url="/blocked/")
def list_services(request, errors=[]):
    try: q=request.GET['q']
    except KeyError: q=''
    items=Service.objects.find(q)
    if items.count()==1: return item_show(request, items[0].pk)
    return _r2r(request,'inventory/service_list.html', {'page':_paginate(request, items),'q':q, 'error_list':errors, 'boxform':BoxForm(),'tipo':'Service'})
@login_required
@permission_required('inventory.change_price', login_url="/blocked/")
def price_edit(request, object_id):
    return edit_object(request, object_id, Price, PriceForm, "price")
######################################################################################
# Garantee Views
######################################################################################
# Client Garantees
######################################################################################

@login_required
@permission_required('inventory.change_clientgarantee', login_url="/blocked/")
def edit_clientgarantee(request, object_id):
    return edit_object(request, object_id, ClientGarantee, ClientGaranteeForm, "clientgarantee")
    
@login_required
@permission_required('inventory.change_clientgarantee', login_url="/blocked/")
def new_clientgarantee(request, object_id):
    sale = get_object_or_404(Sale, pk=object_id)
    error_list={}
    try:
        try: months=sale.item.garanteeoffer_set.filter(price=0)[0].months
        except: months=0
        garantee=ClientGarantee(doc_number=sale.doc_number, date=sale.date, client=sale.client, credit=sale.client.account_group.revenue_account, item=sale.item, quantity=months, serial=sale.serial)
        garantee.save()
        garantee.edit_mode=True
    except Item.DoesNotExist: 
        error_list['item']=[u'La venta debe tener un producto para garantizar.']
        garantee=None
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[garantee],'prefix':'garantee','line_template':"inventory/transaction.html",'error_list':error_list, 'info_list':{}})

######################################################################################
# Vendor Garantees
######################################################################################
@login_required
@permission_required('inventory.change_vendorgarantee', login_url="/blocked/")
def edit_vendorgarantee(request, object_id):
    return edit_object(request, object_id, VendorGarantee, VendorGaranteeForm, "vendorgarantee")
    
@login_required
@permission_required('inventory.change_vendorgarantee', login_url="/blocked/")
def new_vendorgarantee(request, object_id):
    purchase = get_object_or_404(Purchase, pk=object_id)
    garantee=VendorGarantee(doc_number=purchase.doc_number, date=purchase.date, vendor=purchase.vendor, item=purchase.item, serial=purchase.serial)
    garantee.save()
    garantee.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[garantee],'prefix':'garantee','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.change_garanteeoffer', login_url="/blocked/")
def edit_garanteeoffer(request, object_id):
    return edit_object(request, object_id, GaranteeOffer, GaranteeOfferForm, "garanteeoffer",'Garantee Offer')

@login_required
@permission_required('inventory.change_garanteeoffer', login_url="/blocked/")
def delete_garanteeoffer(request, object_id):
    return delete_object(request, object_id, GaranteeOffer, 'garanteeoffer','Garantee Offer')
    
@login_required
@permission_required('inventory.change_garanteeoffer', login_url="/blocked/")
def new_garanteeoffer(request):
    return new_object(request, GaranteeOfferForm, 'garanteeoffer')

@login_required
@permission_required('inventory.view_garanteeoffer', login_url="/blocked/")
def garantee_price(request):
    if (not request.GET['months']) or (not request.GET['item']):
        price=0
        message=None
    else:
        try:
            item=Item.objects.filter(name=request.GET['item'])[0]
            price = GaranteeOffer.objects.filter(item=item.pk, months=request.GET['months'])[0].price
            message=None
        except IndexError: 
            price=0
            message="No garantee of number of months specified was found for this item. The price of the garatee will not be set."
    return _r2r(request,'inventory/garantee_price.html', {'price':price,'message':message})
    
######################################################################################
# Sale Views
######################################################################################
@login_required
@permission_required('inventory.change_sale', login_url="/blocked/")
def edit_sale(request, object_id):
    return edit_object(request, object_id, Sale, SaleForm, "sale")
    
@login_required
@permission_required('inventory.view_sale', login_url="/blocked/")
def list_sales(request, errors={}): # GET ONLY
    return search_and_paginate_transactions(request, Sale,'inventory/sales.html', errors)
@login_required
@permission_required('inventory.change_sale', login_url="/blocked/")
def new_sale(request):
    error_list={}
    try: doc_number=request.POST['doc_number']
    except: doc_number='' 
    if doc_number=='': doc_number=Sale.objects.next_doc_number()
    try: 
        sample=Sale.objects.filter(doc_number=doc_number)[0]
        date=sample.date
        client=sample.client
    except:
        date=datetime.now()
        client=Client.objects.default()
    client=Client.objects.get_or_create_by_name(name=request.POST['client'])
    item=None
    value=0
    cost=0
    try:
        item = Item.objects.fetch(request.POST['item'])
        cost = item.individual_cost
        value = item.price(client)
    except Item.MultipleObjectsReturned: 
        error_list['item']=['There are more than one %ss with the name %s. Try using a bar code.' % ('item', request.POST['item'])]
    except Item.DoesNotExist: 
        if request.POST['item']!='': error_list['item']=["Unable to find '%s' in the list of items." % (request.POST['item'], )]
    if not client: error_list['client']=[unicode('Unable to find a client with the name specified.')]
    # create the sale
    sale=Sale(doc_number=doc_number, date=date, client=client, item=item, cost=cost, value=value, quantity=1)
    sale.save()
    sale.edit_mode=True
    objects=[sale]
    # add any linked items
    if item:
        for link in item.links:
            cost = link.item.individual_cost
            s=Sale(doc_number=doc_number, date=date, client=client, item=link.item, cost=cost, quantity=link.quantity)
            s.save()
            objects.insert(0,s)
    try: 
        offer=sale.item.garanteeoffer_set.filter(price=0)[0]
        garantee=ClientGarantee(doc_number=sale.doc_number, date=sale.date, client=sale.client, item=sale.item, quantity=offer.months, serial=sale.serial)
        garantee.save()
        objects.insert(0,garantee)
    except: pass
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':objects,'prefix':'sale','line_template':"inventory/transaction.html",'error_list':error_list, 'info_list':{}})
    
def get_transaction(request, object_id, edit_mode=False):
    obj = get_object_or_404(Transaction, pk=object_id).subclass
    obj.edit_mode=edit_mode
    if not request.user.has_perm('inventory.change_'+obj.tipo.lower()): return http.HttpResponseRedirect("/blocked/")
    return _r2r(request,'inventory/results.html', {'edit_mode':edit_mode, 'objects':[obj],'prefix':obj.tipo.lower(),'line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.change_clientpayment', login_url="/blocked/")
def add_payment_to_sale(request, object_id):
    obj = get_object_or_404(Sale, pk=object_id)
    doc=Transaction.objects.filter(doc_number=obj.doc_number)
    total=0
    for transaction in doc:
        for entry in transaction.entry_set.filter(account=obj.client):
            if entry.active: total+=entry.value
    payment=ClientPayment(doc_number=obj.doc_number, date=obj.date, credit=obj.client, debit=Setting.get('Payments received account'), value=total)
    payment.save()
    payment.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[payment],'prefix':'clientpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})
    
################################################################################################
#                                     Taxes
################################################################################################
  
@login_required
def add_tax(request, object_id):
    obj = get_object_or_404(Transaction, pk=object_id).subclass
    if not request.user.has_perm('inventory.add_'+obj.tipo.lower()+'tax'): return http.HttpResponseRedirect("/blocked/")
    objects=[]
    rate=TaxRate.objects.get(name=request.POST['rate'])
    total=Entry.objects.filter(transaction__doc_number=obj.doc_number, active=True, account=obj.subclass.account).exclude(transaction__tipo='SaleTax').exclude(transaction__tipo='SaleTax.').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    total=total* obj.account.multiplier
    amount=Decimal(request.POST['amount'])
    percentage=amount/total
    if obj.tipo=='Sale':
        tax=SaleTax(doc_number=obj.doc_number, date=obj.date, debit=obj.client, credit=rate.sales_account, value=amount)
    elif obj.tipo=='Purchase':
        tax=PurchaseTax(doc_number=obj.doc_number, date=obj.date, credit=obj.vendor, debit=rate.purchases_account, value=amount)
    if rate.price_includes_tax=='true':
        doc=Transaction.objects.filter(doc_number=obj.doc_number).exclude(tipo__endswith='Payment').exclude(tipo__endswith='Refund')
        for t in doc:
            t=t.subclass
            t.value-=t.value*percentage
            t.save()
            objects.append(t)
    tax.save()
    tax.edit_mode=True
    objects.append(tax)
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':objects,'prefix':tax.tipo.lower(),'line_template':"inventory/tax.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.change_saletax', login_url="/blocked/")
def edit_saletax(request, object_id):
    return edit_object(request, object_id, SaleTax, SaleTaxForm, "saletax")

@login_required
@permission_required('inventory.change_purchasetax', login_url="/blocked/")
def edit_purchasetax(request, object_id):
    return edit_object(request, object_id, PurchaseTax, PurchaseTaxForm, "purchasetax")
    
@login_required
def get_tax_form(request, object_id):
    obj = get_object_or_404(Transaction, pk=object_id).subclass
    if not request.user.has_perm('inventory.add_'+obj.tipo.lower()+'tax'): return http.HttpResponseRedirect("/blocked/")
    default=obj.account.default_tax_rate
    rates=TaxRate.objects.all()
    total=Entry.objects.filter(transaction__doc_number=obj.doc_number, active=True, account=obj.subclass.account).exclude(transaction__tipo='SaleTax').exclude(transaction__tipo='SaleTax.').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    total=total* obj.account.multiplier
    print "total = " + str(total)
    print "default.price_includes_tax = " + str(default.price_includes_tax)
    print "default.value = " + str(default.value)
    print "total/(default.value+1) = " + str(total/(default.value+1))
    print "total/(default.value+1)*default.value = " + str(total/(default.value+1)*default.value)
    
    print "total*default.value = " + str(total*default.value)
    if default.price_includes_tax:
        amount=total/(default.value+1)*default.value
        print "first route"
    else:
        amount=total*default.value
        print "second route"
    return _r2r(request,'inventory/tax_form.html', {'rates':rates,'default':default,'total':total,'amount':amount})
   
################################################################################################
#                                          Discounts
################################################################################################
def add_discount(request, object_id):
    obj = get_object_or_404(Transaction, pk=object_id).subclass
    if not request.user.has_perm('inventory.add_'+obj.tipo.lower()): return http.HttpResponseRedirect("/blocked/")
    errors={}
    amount=0
    try:
        amount=Decimal(request.POST['discount'])
    except InvalidOperation:
        try:
            total=Entry.objects.filter(transaction__doc_number=obj.doc_number, active=True, account=obj.subclass.account).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
            total=total*obj.subclass.account.multiplier
            amount=total-Decimal(request.POST['total'])
        except:
            errors[_('Amount')]=_("You must enter either the amount of the discount or the discounted total of the transaction.")
    if obj.tipo=='Sale':
        discount=SaleDiscount(doc_number=obj.doc_number, date=obj.date, debit=obj.client.account_group.discounts_account, credit=obj.client, value=amount)
    elif obj.tipo=='Purchase':
        discount=PurchaseDiscount(doc_number=obj.doc_number, date=obj.date, credit=obj.vendor.account_group.discounts_account, debit=obj.vendor, value=amount)
    discount.save()
    discount.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[discount],'prefix':discount.tipo.lower(),'line_template':"inventory/discount.html",'error_list':errors, 'info_list':{}})
    
def edit_salediscount(request, object_id):
    return edit_object(request, object_id, SaleDiscount, SaleDiscountForm, "salediscount")
    
def edit_purchasediscount(request, object_id):
    return edit_object(request, object_id, PurchaseDiscount, PurchaseDiscountForm, "purchasediscount")
#######################################################################################
##                                         Equity Views
#######################################################################################
@login_required
@permission_required('inventory.view_equity', login_url="/blocked/")
def list_equity(request):
    try: q=request.GET['q']
    except KeyError: q=''
    if q=='': page=_paginate(request, Equity.objects.all().order_by('-_date'))
    else: page=_paginate(request, Equity.objects.filter(doc_number=q).order_by('-_date'))
    
    return _r2r(request,'inventory/equity_list.html', {'page':page,'prefix':'transaction','q':q})
@login_required
@permission_required('inventory.change_equity', login_url="/blocked/")
def edit_equity(request, object_id):
    return edit_object(request, object_id, Equity, EquityForm, "equity")
@login_required
@permission_required('inventory.change_equity', login_url="/blocked/")
def new_equity(request):
    error_list={}
    # get the doc number
    try: doc_number=request.POST['doc_number']
    except: doc_number='' 
    if doc_number=='': doc_number=Equity.objects.next_doc_number()
    # get the date
    try: 
        sample=Equity.objects.filter(doc_number=doc_number)[0]
        date=sample.date
    except:
        date=datetime.now()
    try:
        value=Decimal(request.POST['value'])
    except InvalidOperation:
        error_list={_('Value'):[_('This value should be a number')]}
    if len(error_list)==0:
        equity=Equity(
            doc_number=doc_number, 
            date=date,
            value=value,
            )
        equity.save()
        equity.edit_mode=True
        objects=[equity]
    else:
        objects=[]
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':objects,'prefix':'equity','line_template':"inventory/equity.html",'error_list':error_list, 'info_list':{}})
    

#@login_required
#@permission_required('inventory.change_accounting', login_url="/blocked/")
#def edit_accounting(request, object_id):
#    return edit_object(request, object_id, Accounting, AccountingForm, "accounting")
#    
#@login_required
#@permission_required('inventory.view_accounting', login_url="/blocked/")
#def list_accounting(request, errors={}): # GET ONLY
#    return search_and_paginate_transactions(request, Accounting,'inventory/accounting_list.html', errors)
#@login_required
#@permission_required('inventory.change_accounting', login_url="/blocked/")
#def new_accounting(request):
#    error_list={}
#    # get the doc number
#    try: doc_number=request.POST['doc_number']
#    except: doc_number='' 
#    if doc_number=='': doc_number=Accounting.objects.next_doc_number()
#    # get the date
#    try: 
#        sample=Accounting.objects.filter(doc_number=doc_number)[0]
#        date=sample.date
#    except:
#        date=datetime.now()
#    if len(error_list)==0:
#        transaction=Accounting(
#            doc_number=doc_number, 
#            date=date, 
#            debit_account=DEFAULT_ACCOUNTING_DEBIT_ACCOUNT, 
#            credit_account=DEFAULT_ACCOUNTING_CREDIT_ACCOUNT)
#        transaction.save()
#        objects=[transaction]
#    else:
#        objects=[]
#    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':objects,'prefix':'accounting','line_template':"inventory/accounting.html",'error_list':error_list, 'info_list':{}})
#    
 
######################################################################################
# Return Views
######################################################################################
@login_required
@permission_required('inventory.change_salereturn', login_url="/blocked/")
def edit_salereturn(request, object_id):
    return edit_object(request, object_id, SaleReturn, SaleForm, "salereturn")
    
@login_required
@permission_required('inventory.change_salereturn', login_url="/blocked/")
def new_salereturn(request, object_id):
    sale = get_object_or_404(Sale, pk=object_id)
    salereturn=SaleReturn(
        doc_number=sale.doc_number,
        date=sale.date,
        client=sale.client,
        item=sale.item,
        quantity=-sale.quantity,
        serial=sale.serial,
        value=-sale.value,
        cost=-sale.cost,
    )
    salereturn.save()
    salereturn.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[salereturn],'prefix':'salereturn','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

########################################################################################
@login_required
@permission_required('inventory.change_purchasereturn', login_url="/blocked/")
def edit_purchasereturn(request, object_id):
    return edit_object(request, object_id, PurchaseReturn, PurchaseForm, "purchasereturn")
    
@login_required
@permission_required('inventory.change_purchasereturn', login_url="/blocked/")
def new_purchasereturn(request, object_id):
    purchase = get_object_or_404(Purchase, pk=object_id)
    
    purchasereturn=PurchaseReturn(
        doc_number=purchase.doc_number, 
        date=purchase.date, 
        value=-purchase.value,
        item=purchase.item, 
        quantity=-purchase.quantity, 
        serial=purchase.serial,
        vendor=purchase.vendor, 
    )
    purchasereturn.save()
    purchasereturn.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[purchasereturn],'prefix':'purchasereturn','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

######################################################################################
# Refunds
######################################################################################

@login_required
@permission_required('inventory.change_clientrefund', login_url="/blocked/")
def edit_clientrefund(request, object_id):
    return edit_object(request, object_id, ClientRefund, ClientPaymentForm, "clientrefund")
    
@login_required
@permission_required('inventory.change_clientrefund', login_url="/blocked/")
def new_clientrefund(request, object_id):
    payment = get_object_or_404(ClientPayment, pk=object_id)
    refund=ClientRefund(
        doc_number=payment.doc_number, 
        date=payment.date, 
        value=-payment.value,
        credit=payment.credit,  
    )
    refund.save()
    refund.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[refund],'prefix':'clientrefund','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

######################################################################################
# Vendor Refunds
######################################################################################
@login_required
@permission_required('inventory.change_vendorrefund', login_url="/blocked/")
def edit_vendorrefund(request, object_id):
    return edit_object(request, object_id, VendorRefund, VendorPaymentForm, "vendorrefund")
    
@login_required
@permission_required('inventory.change_vendorrefund', login_url="/blocked/")
def new_vendorrefund(request, object_id):
    payment = get_object_or_404(VendorPayment, pk=object_id)
    refund=VendorRefund(
        doc_number=payment.doc_number, 
        date=payment.date, 
        value=-payment.value,
        debit=payment.debit,  
    )
    refund.save()
    refund.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[refund],'prefix':'vendorrefund','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

######################################################################################
# Payment Views
######################################################################################
# Client Payments
######################################################################################
@login_required
@permission_required('inventory.change_clientpayment', login_url="/blocked/")
def edit_clientpayment(request, object_id):
    return edit_object(request, object_id, ClientPayment, ClientPaymentForm, "clientpayment")
    
@login_required
@permission_required('inventory.change_clientpayment', login_url="/blocked/")
def new_clientpayment(request):
    doc_number=request.POST['doc_number']
    try: 
        sample = Sale.objects.filter(doc_number=doc_number)[0]
        date = sample.date
        client = sample.client
    except:
        date = datetime.now()
        client = Client.objects.default()
    try: 
        if request.POST['client']: 
            client = Client.objects.get(name=request.POST['client'])
    except:pass
    clientpayment=ClientPayment(doc_number=doc_number, date=date, account=client)
    clientpayment.save()
    clientpayment.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[clientpayment],'prefix':'clientpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})
######################################################################################
# Vendor Payments
######################################################################################
@login_required
@permission_required('inventory.change_vendorpayment', login_url="/blocked/")
def edit_vendorpayment(request, object_id):
    return edit_object(request, object_id, VendorPayment, VendorPaymentForm, "vendorpayment")
    
@login_required
@permission_required('inventory.change_vendorpayment', login_url="/blocked/")
def new_vendorpayment(request):
    try: doc_number=request.POST['doc_number']
    except: doc_number='7777' # TODO This should grab the next available doc_number
    try: 
        sample = Purchase.objects.filter(doc_number=doc_number)[0]
        date = sample.date
        vendor = sample.vendor
    except:
        date = datetime.now()
        vendor = Vendor.objects.default()
    try: 
        if request.POST['vendor']: vendor = Vendor.objects.get(name=request.POST['vendor'])
    except:pass
    vendorpayment=VendorPayment(doc_number=doc_number, date=date, source=PAYMENTS_MADE_ACCOUNT, dest=vendor)
    vendorpayment.save()
    vendorpayment.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[vendorpayment],'prefix':'vendorpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})
    
    
@login_required
@permission_required('inventory.add_tax', login_url="/blocked/")
def new_tax(request):
    doc_number=request.POST['doc_number']
    try: 
        sample = Sale.objects.filter(doc_number=doc_number)[0]
        date = sample.date
        client = sample.client
    except:
        date = datetime.now()
        client = Client.objects.default()
    try: 
        if request.POST['client']:
            client = Client.objects.get(name=request.POST['client'])
    except:pass
    clientpayment=ClientPayment(doc_number=doc_number, date=date, source=client, dest=PAYMENTS_RECEIVED_ACCOUNT)
    clientpayment.save()
    clientpayment.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[clientpayment],'prefix':'clientpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

######################################################################################
# Transaction Views
######################################################################################
@login_required
@permission_required('inventory.change_transaction', login_url="/blocked/")
def transaction_list(request, errors={}): # GET ONLY
    if 'tipo' in request.GET: 
        if request.GET['tipo']=='Sale': return search_and_paginate_transactions(request, Transaction, template='inventory/sales.html')
        if request.GET['tipo']=='Purchase': return search_and_paginate_transactions(request, Transaction, template='inventory/purchases.html')
        if request.GET['tipo']=='Count': return search_and_paginate_transactions(request, Transaction, template='inventory/counts.html')
    return search_and_paginate_transactions(request, Transaction)
@login_required
def delete_transaction(request, object_id):
    return delete_object(request, object_id, Transaction, 'transaction')
@login_required
def mark_transaction(request, object_id, attr, value):
    obj = get_object_or_404(Transaction, pk=object_id).subclass
    if not request.user.has_perm('inventory.change_sale') and obj.tipo=='Sale': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_purchase') and obj.tipo=='Purchase': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_count') and obj.tipo=='Count': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_process') and obj.tipo=='Process': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_production') and obj.tipo=='Production': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_productionorder') and obj.tipo=='ProductionOrder': return http.HttpResponseRedirect("/blocked/")
    if obj.tipo=='Process' and attr in ['delivered','active']:
        return _r2r(request,'inventory/results.html', {'objects':[obj],'error_list':{'Process':[_('Cannot be marked delivered or active'),]}, 'info_list':[]})
    if obj.tipo=='Job':
        if attr in ['delivered','active' ] and obj.quantity < 0 and not request.user.has_perm('production.start_production'):
            return _r2r(request,'inventory/results.html', {'objects':[obj],'error_list':{'Process':[_('You do not have sufficient rights to start production'),]}, 'info_list':[]})
        if attr in ['delivered','active' ] and obj.quantity > 0 and not request.user.has_perm('production.finish_production'):
            return _r2r(request,'inventory/results.html', {'objects':[obj],'error_list':{'Process':[_('You do not have sufficient rights to finish production'),]}, 'info_list':[]})
    setattr(obj, attr, value)
    obj.save()
    return _r2r(request,'inventory/results.html', {'objects':[obj],'error_list':{}, 'info_list':[]})
def deliver_transaction(request, object_id):
    return mark_transaction(request, object_id, 'delivered', True)
def undeliver_transaction(request, object_id):
    return mark_transaction(request, object_id, 'delivered', False)
def activate_transaction(request, object_id):
    return mark_transaction(request, object_id, 'active', True)
def deactivate_transaction(request, object_id):
    return mark_transaction(request, object_id, 'active', False)
@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def movements_report(request):       
    transactions = Transaction.objects.all().order_by('-_date')
    try:transactions=transactions.filter(doc_number__icontains=request.GET['q'])
    except: pass
    try:transactions=transactions.filter(_date__gte=request.GET['start'])
    except: pass
    try:transactions=transactions.filter(_date__lt=request.GET['end'])
    except: pass
    try:report=Setting.get('Movements report')
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
#        request.GET['q']=doc_number
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (Setting.get('Movements report').name,))]}
        return list_sales(request, errors=errors)
    return render_string_to_pdf(request, Template(report.body), {'transactions':transactions, 'user':request.user})  

@login_required
@permission_required('inventory.add_cash_closing', login_url="/blocked/")
def new_cash_closing(request):
    form=SearchForm(request.GET)
    form.is_valid()
    start=form.cleaned_data['start']
    end=form.cleaned_data['end']
    cash_closings=CashClosing.objects.all()
    if not start and not end:
        from datetime import datetime
        start=datetime.date(datetime.now())
        end=start+timedelta(days=1)
    if start: cash_closings=cash_closings.filter(_date__gte=start)
    if end:
        deadline = end + timedelta(days=1)
        cash_closings=cash_closings.filter(_date__lt=deadline)
        cash=Entry.objects.filter(account=Setting.get('Cash account'), date__lt=dt(deadline)).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    if cash_closings.count() == 0:
        doc_number=CashClosing.objects.next_doc_number()
        c=CashClosing(doc_number=doc_number, date=start, value=cash-Setting.get('Starting cash account balance'))
        c.save()
        c.edit_mode=True
        return _r2r(request,'inventory/results.html', {'objects':[c],'prefix':'cash_closing','line_template':"inventory/cash_closing.html",'error_list':{}, 'info_list':{}})
    else:
        return _r2r(request,'inventory/results.html', {'objects':[],'prefix':'cash_closing','line_template':"inventory/cash_closing.html",'error_list':{_('CashClosing'):[_('There can only be one cash_closing per day.'),]}, 'info_list':{}})
    
@login_required
@permission_required('inventory.change_cash_closing', login_url="/blocked/")
def edit_cash_closing(request, object_id):    
    return edit_object(request, object_id, CashClosing, CashClosingForm, "cash_closing")

def cash_closing_report(request, object_id):
    cash_closing = get_object_or_404(CashClosing, pk=object_id)
    try:report=Setting.get('Cash closing report')
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (Setting.get('Cash closing report').name,))]}
        return item_list(request, errors=errors)
    return render_string_to_pdf(request, Template(report.body), {
        'start':cash_closing.start,
        'end':cash_closing.end,
        'groups':cash_closing.account_groups,
        'sales':cash_closing.sale_entries,
        'payments':cash_closing.payments,
        'paid_sales':cash_closing.paid_sales,
        'unpaid_sales':cash_closing.unpaid_sales,
        'groups_by_series':cash_closing.groups_by_series,
        'grouped_payments':cash_closing.payments_by_timing,
        'user':request.user,
        'settings.COMPANY_NAME':Setting.get('Company name'),
        'company_name':Setting.get('Company name'),
        'revenue':cash_closing.revenue,        
        'discount':cash_closing.discount,        
        'totalrevenue':cash_closing.revenue-cash_closing.discount,
        'earnings':cash_closing.earnings,
        'expense':cash_closing.expense,
        'tax':cash_closing.tax,
        'final_cash':cash_closing.ending_cash,
        'initial_cash':cash_closing.starting_cash,
        'revenue_check':cash_closing.revenue_check,
        'cash_check':cash_closing.cash_check,
        'paymentstotal':cash_closing.paymentstotal,
    })  
@login_required
@permission_required('inventory.view_cashclosing', login_url="/blocked/")
def list_cashclosing(request):
    try: q=request.GET['q']
    except KeyError: q=''
    if q=='': page=_paginate(request, CashClosing.objects.all().order_by('-_date'))
    else: page=_paginate(request, CashClosing.objects.filter(doc_number=q).order_by('-_date'))
    
    return _r2r(request,'inventory/cashclosing_list.html', {'page':page,'prefix':'transaction','q':q})
######################################################################################
# Transfer Views
######################################################################################
@login_required
@permission_required('inventory.view_transfer', login_url="/blocked/")
def list_transfers(request): # GET ONLY
    return search_and_paginate_transactions(request, Transfer,'inventory/transfers.html')

@login_required
@permission_required('inventory.change_transfer', login_url="/blocked/")
def edit_transfer(request, object_id):
    return edit_object(request, object_id, Transfer, TransferForm, "transfer")

@login_required
@permission_required('inventory.change_transfer', login_url="/blocked/")
def new_transfer(request):
    error_list={}
    item=None
    cost=0
    try: doc_number=request.POST['doc_number']
    except: doc_number='' 
    if doc_number=='': doc_number=Transfer.objects.next_doc_number()
    try: 
        sample=Transfer.objects.filter(doc_number=doc_number)[0]
        date=sample.date
    except:
        date=datetime.now()
    try: account=Site.objects.get(name=request.POST['client'])
    except: 
        account=None
        error_list['client']=[unicode('Unable to find a site with the name specified.')]
    try:
        item=Item.objects.fetch(request.POST['item'])
        cost=item.cost
    except Item.MultipleObjectsReturned: 
        error_list['item']=['There are more than one %ss with the name %s. Try using a bar code.' % ('item', request.POST['item'])]
    except Item.DoesNotExist: 
        if request.POST['item']!='': error_list['item']=["Unable to find '%s' in the list of items." % (request.POST['item'], )]
    transfer=Transfer(doc_number=doc_number, date=date, account=account, item=item, cost=cost)
    if len(error_list)==0:
        transfer.save()
    transfer.edit_mode=True
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[transfer],'prefix':'transfer','line_template':"inventory/transaction.html",'error_list':error_list, 'info_list':{}})

@login_required
@permission_required('inventory.add_linkeditem', login_url="/blocked/")
def new_linkeditem(request, object_id):
    obj = get_object_or_404(Item, pk=object_id)
    error_list={}
    item=None
    try:
        item=Item.objects.fetch(request.POST['item'])
        link=LinkedItem(parent=obj, child=item, quantity=1)
        link.save()  
    except Item.MultipleObjectsReturned: 
        error_list['item']=['There are more than one %ss with the name %s. Try using a bar code.' % ('item', request.POST['item'])]
    except Item.DoesNotExist: 
        error_list['item']=["Unable to find '%s' in the list of items." % (request.POST['item'], )]        
    if not error_list: 
        info_list=['The linked item has been added successfully.',]
        return _r2r(request,'inventory/linkeditem.html', {'object':link,'error_list':{}, 'info_list':{}})
    else: return _r2r(request,'inventory/results.html', {'object':[],'error_list':{}, 'info_list':{}})
        
    
@login_required
@permission_required('inventory.change_linkeditem', login_url="/blocked/")
def edit_linkeditem(request, object_id):
    return edit_object(request, object_id, LinkedItem, LinkedItemForm, "linkeditem",'Linked Item')

@login_required
@permission_required('inventory.delete_linkeditem', login_url="/blocked/")
def delete_linkeditem(request, object_id):
    return delete_object(request, object_id, LinkedItem, 'linkeditem','Linked Item')
 
################################################################################################
# Login procedure
################################################################################################
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = Setting.get("Login redirect url")
            
            # Heavier security check -- redirects to http://example.com should 
            # not be allowed, but things like /view/?param=http://example.com 
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = Setting.get("Login redirect url")
            
            # Okay, security checks complete. Log the user in.
            user=form.get_user()
            auth_login(request, user)

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            profile=user.get_profile()
#            profile.tabs.all().delete()
            for t in Tab.objects.all():
                if user.has_perm(t.perm):
                    profile.tabs.add(t)
                elif t in profile.tabs.all(): # Here we assume that he doesnt have rights
                    profile.tabs.remove(t)
                    
            return HttpResponseRedirect(redirect_to)

    else:
        form = authentication_form(request)
    
    request.session.set_test_cookie()
    
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))
