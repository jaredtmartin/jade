from jade.inventory.models import Count, Sale, Purchase, INVENTORY_ACCOUNT, CASH_ACCOUNT, REVENUE_ACCOUNT, TAX_ACCOUNT, EXPENSE_ACCOUNT
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
#from jade.settings import settings.APP_LOCATION, settings.COMPANY_NAME, settings.CORTE_REPORT_NAME, settings.MOVEMENTS_REPORT_NAME, settings.PRICE_REPORT_NAME, settings.INVENTORY_REPORT_NAME, settings.MEDIA_URL, settings.APP_LOCATION, settings.RECEIPT_REPORT_NAME_SUFFIX, settings.RECEIPT_REPORT_NAME_PREFIX, settings.COUNT_SHEET_REPORT_NAME, settings.LABEL_SHEET_REPORT_NAME
from jade import settings

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
    extra_context.update({'objects':[obj],'form':updated_form,'info_list':info_list,'error_list':error_list,'prefix':prefix,'line_template':"inventory/transaction.html"})
    return _r2r(request,'inventory/results.html', extra_context)
    
def delete_object(request, object_id, model, prefix, tipo=None):
    obj = get_object_or_404(model, pk=object_id)
    if not request.user.has_perm('inventory.delete_'+obj.tipo.lower()): return http.HttpResponseRedirect("/blocked/")
    if not tipo: tipo=obj.get_tipo_display()
    obj.delete()
    info_list=['The '+tipo+' has been deleted successfully.',]
    return _r2r(request,'inventory/results.html', {'error_list':{}, 'info_list':info_list})

def new_object(request, form, prefix, template='', tipo=None, extra_context={}):
    if tipo and not request.user.has_perm('inventory.change_'+tipo.lower()): return http.HttpResponseRedirect("/blocked/")
    if request.POST:
        f = form(request.POST)
        print "adadad"
        if f.is_valid():      
            print "valid"
            print "tipo = " + str(tipo)
            if tipo:obj=f.save(tipo=tipo)
            else:obj=f.save()
            updated_form=form(instance=obj, prefix=prefix+'-'+str(obj.pk))
            info_list=['The %s has been created successfully.'% tipo, ]
            error_list={}
        else:
            print "invalid"      
            info_list=[]
            obj=None
            print "f.errors = " + str(f.errors)
            error_list=f.errors
            updated_form=None
        if not tipo: tipo=prefix
        extra_context.update({'objects':[obj],'edit_mode':True, 'form':updated_form,'info_list':info_list,'error_list':error_list,'prefix':tipo,'line_template':"inventory/"+prefix+".html"})
        return _r2r(request,'inventory/results.html', extra_context)
    else:
        form=form(prefix=prefix+'-')
        if not tipo: tipo=prefix
        extra_context.update({'form':form,'prefix':tipo})
        return _r2r(request,template, extra_context)
    
def search_entries(user, form, tipo=None):
    entries = Entry.objects.all().order_by('-date')
    if tipo: entries=entries.filter(tipo=tipo)
    if not form.cleaned_data['q']=='': entries=entries.filter(transaction__doc_number=form.cleaned_data['q'])
    if form.cleaned_data['start']: entries=entries.filter(date__gte=form.cleaned_data['start'])
    if form.cleaned_data['end']: entries=entries.filter(date__lt=form.cleaned_data['end']+timedelta(days=1))
    return entries

def search_transactions(user, form, transactions, strict=True):
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
def list_purchases(request): # GET ONLY
    return search_and_paginate_transactions(request, Purchase,'inventory/purchases.html')

@login_required
@permission_required('inventory.change_purchase', login_url="/blocked/")
def edit_purchase(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Purchase, PurchaseForm, "purchase")

@login_required
@permission_required('inventory.change_purchase', login_url="/blocked/")
def new_purchase(request): # AJAX POST ONLY
    error_list={}
    cost=0
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
        cost=item.cost
    except Item.MultipleObjectsReturned: 
        error_list['item']=['There are more than one %ss with the name %s. Try using a bar code.' % ('item', request.POST['item'])]
    except Item.DoesNotExist: 
        if request.POST['item']!='': error_list['item']=["Unable to find '%s' in the list of items." % (request.POST['item'], )]
    if vendor:
        if vendor.tax_group.price_includes_tax: cost = cost/(vendor.tax_group.value+1)
        tax=cost*vendor.tax_group.value
    else:
        error_list['vendor']=[unicode('Unable to find a vendor with the name specified.')]
    purchase=Purchase(doc_number=doc_number, date=date, vendor=vendor, item=item, cost=cost, tax=tax)
    purchase.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[purchase],'prefix':'purchase','line_template':"inventory/transaction.html",'error_list':error_list, 'info_list':{}})

@login_required
@permission_required('inventory.change_vendorpayment', login_url="/blocked/")
def add_payment_to_purchase(request, object_id): # AJAX POST ONLY
    obj = get_object_or_404(Purchase, pk=object_id)
    doc=Transaction.objects.filter(doc_number=obj.doc_number)
    total=0
    for transaction in doc:
        for entry in transaction.entry_set.filter(account=obj.vendor):
            if entry.active: total-=entry.value
    payment=VendorPayment(doc_number=obj.doc_number, date=obj.date, source=PAYMENTS_MADE_ACCOUNT, dest=obj.vendor, value=total)
    payment.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[payment],'prefix':'vendorpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})
  

def delete_purchase(request, object_id):
    return delete_object(request, object_id, Purchase, 'purchase')
######################################################################################
# Ajax Views
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
@permission_required('inventory.view_tax_group', login_url="/blocked/")
def ajax_tax_group_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/ajax_list.html', {'object_list':TaxGroup.objects.filter(name__icontains=q),'q':q})

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
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), dest=result, link_callback=fetch_resources)
    if not pdf.err:
        return http.HttpResponse(result.getvalue(), mimetype='application/pdf')
    return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))
    
def render_string_to_pdf(template, context_dict):
    context = Context(context_dict)
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
    return render_string_to_pdf(Template(report.body), context)
def doc_inactive(doc):
    for line in doc:
        if line.active or line.delivered: return False
    return True
@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def quote(request, doc_number):
    doc=Sale.objects.filter(doc_number=doc_number)
    if doc.count()==0: return fallback_to_transactions(request, doc_number, _('Unable to find sales with the specified document number.'))
    try:report=Report.objects.get(name=settings.QUOTE_TEMPLATE_NAME)
    except Report.DoesNotExist: 
        return fallback_to_transactions(request, doc_number, _('Unable to find a report template with the name "%s"') % settings.QUOTE_TEMPLATE_NAME)
    tax=charge=discount=0
    for t in doc:
        s=t.subclass
        try: tax+=s.tax
        except AttributeError: pass
        try: charge+=s.charge
        except AttributeError: pass
        try: discount+=s.discount
        except AttributeError: pass
    try:
        request.GET['test']
        return render_string_to_pdf(Template(report.body), {'doc':doc, 'watermark_filename':report.watermark_url,'tax':tax, 'charge':charge, 'discount':discount})
    except:
        return render_string_to_pdf(Template(report.body), {'watermark_filename':None, 'doc':doc, 'tax':tax, 'charge':charge, 'discount':discount})

@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def sale_receipt(request, doc_number):
    doc=Sale.objects.filter(doc_number=doc_number)
    if doc.count()==0: return fallback_to_transactions(request, doc_number, _('Unable to find sales with the specified document number.'))
    if doc_inactive(doc): return quote(request, doc_number)
    try:report=Report.objects.get(name=settings.RECEIPT_REPORT_NAME_PREFIX+doc[0].client.tax_group.name+settings.RECEIPT_REPORT_NAME_SUFFIX)
    except Report.DoesNotExist: 
        return fallback_to_transactions(request, doc_number, _('Unable to find a report template with the name "%s"') % (settings.RECEIPT_REPORT_NAME_PREFIX+doc[0].client.tax_group.name+settings.RECEIPT_REPORT_NAME_SUFFIX,))
    tax=charge=discount=0
    for t in doc:
        s=t.subclass
        try: tax+=s.tax
        except AttributeError: pass
        try: charge+=s.charge
        except AttributeError: pass
        try: discount+=s.discount
        except AttributeError: pass
    try:
        request.GET['test']
        return render_string_to_pdf(Template(report.body), {'doc':doc, 'watermark_filename':report.watermark_url,'tax':tax, 'charge':charge, 'discount':discount})
    except:
        return render_string_to_pdf(Template(report.body), {'watermark_filename':None, 'doc':doc, 'tax':tax, 'charge':charge, 'discount':discount})

@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def garantee_report(request, doc_number):
    doc=ClientGarantee.objects.filter(doc_number=doc_number)
    if doc.count()==0: return fallback_to_transactions(request, doc_number, _('Unable to find sales with the specified document number.'))
    try:report=Report.objects.get(name=settings.GARANTEE_REPORT_NAME)
    except Report.DoesNotExist: 
        return fallback_to_transactions(request, doc_number, _('Unable to find a report template with the name "%s"') % settings.GARANTEE_REPORT_NAME)
    return render_string_to_pdf(Template(report.body), {'doc':doc})

@login_required
@permission_required('inventory.view_receipt', login_url="/blocked/")
def count_sheet(request, doc_number):
    doc=Count.objects.filter(doc_number=doc_number)
    if doc.count()==0: return fallback_to_transactions(request, doc_number, 'Unable to find counts with the specified document number.')
    try:report=Report.objects.get(name=settings.COUNT_SHEET_REPORT_NAME)
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
        request.GET['q']=doc_number
        errors={'Report':[unicode('Unable to find a report template with the name"%s"' % (settings.COUNT_SHEET_REPORT_NAME,))]}
        return transaction_list(request, errors=errors)
    total=0
    for t in doc:
        s=t.subclass
        try: total+=s.cost
        except AttributeError: pass
    return render_string_to_pdf(Template(report.body), {'watermark_filename':report.watermark_url, 'doc':doc,'total':total})
       
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
            if x>=settings.LABELS_PER_PAGE:
                p.showPage()
                x-=settings.LABELS_PER_PAGE
            p.drawImage(filepath, x%settings.LABELS_PER_LINE*150, p._pagesize[1]-(x/settings.LABELS_PER_LINE+1)*75)
            x+=1
    p.showPage()
    p.save()
    return response

######################################################################################
# Count Views
######################################################################################
@login_required
@permission_required('inventory.view_count', login_url="/blocked/")
def list_counts(request): # GET ONLY
    try: q=request.GET['q']
    except KeyError: q=''
    if q=='': page=_paginate(request, Count.objects.all().order_by('-_date'))
    else: page=_paginate(request, Count.objects.filter(doc_number=q).order_by('-_date'))
    
    return _r2r(request,'inventory/counts.html', {'page':page,'prefix':'transaction','q':q})

@login_required
@permission_required('inventory.change_count', login_url="/blocked/")
def edit_count(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Count, CountForm, "count")
    
@login_required
@permission_required('inventory.change_count', login_url="/blocked/")
def new_count(request): # AJAX POST ONLY
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
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[count],'prefix':'count','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.change_count', login_url="/blocked/")
def delete_count(request, object_id):
    return delete_object(request, object_id, Count, 'count')

@login_required
@permission_required('inventory.post_count', login_url="/blocked/")
def post_count(request, object_id):
    count = get_object_or_404(Count, pk=object_id)
    success=count.post()
    if success: info_list=['The count has been posted successfully.',]
    else: info_list=[]
    return _r2r(request,'inventory/results.html', {'objects':[count],'prefix':'count','line_template':"inventory/transaction.html", 'error_list':count.errors, 'info_list':info_list})
######################################################################################
# Accounts Views
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

@login_required
@permission_required('inventory.view_branch', login_url="/blocked/")
def branch_list(request):
    try: q=request.GET['q']
    except KeyError: q=''
    return _r2r(request,'inventory/branch_list.html', {'page':_paginate(request, Branch.objects.filter(name__icontains=q)),'q':q})

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
    total=0
    for entry in entries:
        total+=entry.value
        entry.total=total    
    if not request.user.has_perm('inventory.view_client') and account.tipo=="Client": return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.view_vendor') and account.tipo=="Vendor": return http.HttpResponseRedirect("/blocked/")
    return render_report(request, settings.ACCOUNT_STATEMENT_REPORT_NAME, {'account':account,'entries':entries})
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
    print "asdjhaskdjhaskjdh"
    return new_object(request, AccountForm, "account", 'inventory/account_show.html', tipo='Account', extra_context={'tipo':'account'})

######################################################################################
# Item Views
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
    try:report=Report.objects.get(name=settings.LOW_STOCK_REPORT_NAME)
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (settings.LOW_STOCK_REPORT_NAME,))]}
        return low_stock(request, errors=errors)
    return render_string_to_pdf(Template(report.body), {'items':items, 'user':request.user})  
    


@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def price_report(request):
    try: q=request.GET['q']
    except KeyError: q=''
    items=Item.objects.find(q)
    print "items = " + str(items)
    try:report=Report.objects.get(name=settings.PRICE_REPORT_NAME)
    except Report.DoesNotExist:
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (settings.PRICE_REPORT_NAME,))]}
        return item_list(request, errors=errors)
    return render_string_to_pdf(Template(report.body), {'items':items, 'user':request.user})
@login_required
@permission_required('inventory.view_item', login_url="/blocked/")
def inventory_report(request):
    try: q=request.GET['q']
    except KeyError: q=''
    items=Item.objects.find(q)
    print "items = " + str(items)
    try:report=Report.objects.get(name=settings.INVENTORY_REPORT_NAME)
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (settings.INVENTORY_REPORT_NAME,))]}
        return item_list(request, errors=errors)
    return render_string_to_pdf(Template(report.body), {'items':items, 'user':request.user})  
    
    
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
                'entry_page': _paginate(request, Entry.objects.filter(item=item, account=INVENTORY_ACCOUNT)),
                'form': form,
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
    print "item = " + str(item)
    print "request.POST = " + str(request.POST)
    print "len(request.FILES) = " + str(len(request.FILES))
    form = ItemImageForm(request.POST, request.FILES)
    print "form = " + str(form)
    result=form.is_valid()
    print "result = " + str(result)
    if result: 
        item.image=form.cleaned_data['image']
        item.save()
        print "form.cleaned_data['image'] = " + str(form.cleaned_data['image'])
    return _r2r(request,'inventory/item_image.html', {'item':item})
        
@login_required
@permission_required('inventory.create_item', login_url="/blocked/")
def new_item(request):
    return new_object(request, ItemForm, "item", 'inventory/item_show.html', tipo='Item')

@login_required
@permission_required('inventory.change_item', login_url="/blocked/")
def edit_item(request, object_id):
    return edit_object(request, object_id, Item, ItemForm, "item")
    
######################################################################################
# Price Views
######################################################################################
@login_required
@permission_required('inventory.change_price', login_url="/blocked/")
def price_list(request): # GET ONLY
    try: q=request.GET['q']
    except KeyError: q=''
    page=_paginate(request, Price.objects.filter(item__name__icontains=q))
    forms = [PriceForm(instance=price, prefix="form-"+str(price.pk)) for price in page.object_list]
    return _r2r(request,'inventory/price_list.html', {
        'page':page,
        'price_forms':forms,
        'q':q,
    })

@login_required
@permission_required('inventory.change_garanteeoffer', login_url="/blocked/")
def price_edit(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Price, PriceForm, "price")
######################################################################################
# Garantee Views
######################################################################################
# Client Garantees
######################################################################################

@login_required
@permission_required('inventory.change_clientgarantee', login_url="/blocked/")
def edit_clientgarantee(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, ClientGarantee, ClientGaranteeForm, "clientgarantee")
    
@login_required
@permission_required('inventory.change_clientgarantee', login_url="/blocked/")
def new_clientgarantee(request, object_id): # AJAX POST ONLY
    sale = get_object_or_404(Sale, pk=object_id)
    try: months=sale.item.garanteeoffer_set.filter(price=0)[0]
    except: months=0
    garantee=ClientGarantee(doc_number=sale.doc_number, date=sale.date, client=sale.client, item=sale.item, quantity=months, serial=sale.serial)
    garantee.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[garantee],'prefix':'garantee','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.change_clientgarantee', login_url="/blocked/")
def delete_clientgarantee(request, object_id):
    return delete_object(request, object_id, ClientGarantee, 'clientgarantee')

######################################################################################
# Vendor Garantees
######################################################################################
@login_required
@permission_required('inventory.change_vendorgarantee', login_url="/blocked/")
def edit_vendorgarantee(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, VendorGarantee, VendorGaranteeForm, "vendorgarantee")
    
@login_required
@permission_required('inventory.change_vendorgarantee', login_url="/blocked/")
def new_vendorgarantee(request, object_id): # AJAX POST ONLY
    purchase = get_object_or_404(Purchase, pk=object_id)
    garantee=VendorGarantee(doc_number=purchase.doc_number, date=purchase.date, vendor=purchase.vendor, item=purchase.item, serial=purchase.serial)
    garantee.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[garantee],'prefix':'garantee','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.change_vendorgarantee', login_url="/blocked/")
def delete_vendorgarantee(request, object_id):
    return delete_object(request, object_id, VendorGarantee, 'vendorgarantee')

@login_required
@permission_required('inventory.change_garanteeoffer', login_url="/blocked/")
def edit_garanteeoffer(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, GaranteeOffer, GaranteeOfferForm, "garanteeoffer",'Garantee Offer')

@login_required
@permission_required('inventory.change_garanteeoffer', login_url="/blocked/")
def delete_garanteeoffer(request, object_id): # AJAX POST ONLY
    return delete_object(request, object_id, GaranteeOffer, 'garanteeoffer','Garantee Offer')
    
@login_required
@permission_required('inventory.change_garanteeoffer', login_url="/blocked/")
def new_garanteeoffer(request): # AJAX POST ONLY
    return new_object(request, GaranteeOfferForm, 'garanteeoffer')

@login_required
@permission_required('inventory.view_garanteeoffer', login_url="/blocked/")
def garantee_price(request): # AJAX GET ONLY
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
def edit_sale(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Sale, SaleForm, "sale")
    
@login_required
@permission_required('inventory.view_sale', login_url="/blocked/")
def list_sales(request, errors={}): # GET ONLY
    return search_and_paginate_transactions(request, Sale,'inventory/sales.html', errors)
@login_required
@permission_required('inventory.change_sale', login_url="/blocked/")
def new_sale(request): # AJAX POST ONLY
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
    try: client=Client.objects.get_or_create_by_name(name=request.POST['client'])
    except:pass
    print "client = " + str(client)
    item=None
    tax=price=cost=0
    try:
        item = Item.objects.fetch(request.POST['item'])
        cost = item.cost
        price = item.price(client)
        if client.tax_group.price_includes_tax:
            price = price/(client.tax_group.value+1)
        tax = item.price(client)*client.tax_group.value
    except Item.MultipleObjectsReturned: 
#        raise forms.ValidationError('There are more than one %ss with the name %s. Try using a bar code.' % (name, data))
        error_list['item']=['There are more than one %ss with the name %s. Try using a bar code.' % ('item', request.POST['item'])]
    except Item.DoesNotExist: 
        if request.POST['item']!='': error_list['item']=["Unable to find '%s' in the list of items." % (request.POST['item'], )]
#        raise forms.ValidationError("Unable to find '%s' in the list of items." % (data, ))
    if not client: error_list['client']=[unicode('Unable to find a client with the name specified.')]
    sale=Sale(doc_number=doc_number, date=date, client=client, item=item, cost=cost, price=price, tax=tax)
    sale.save()
    objects=[sale]
    try: 
        offer=sale.item.garanteeoffer_set.filter(price=0)[0]
        garantee=ClientGarantee(doc_number=sale.doc_number, date=sale.date, client=sale.client, item=sale.item, quantity=offer.months, serial=sale.serial)
        garantee.save()
        objects.insert(0,garantee)
    except: pass
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':objects,'prefix':'sale','line_template':"inventory/transaction.html",'error_list':error_list, 'info_list':{}})
    
def get_transaction(request, object_id, edit_mode=False):
    obj = get_object_or_404(Transaction, pk=object_id).subclass
    if not request.user.has_perm('inventory.change_'+obj.tipo.lower()): return http.HttpResponseRedirect("/blocked/")
    return _r2r(request,'inventory/results.html', {'edit_mode':edit_mode, 'objects':[obj],'prefix':obj.tipo.lower(),'line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

def delete_sale(request, object_id):
    return delete_object(request, object_id, Sale, 'sale')

@login_required
@permission_required('inventory.change_clientpayment', login_url="/blocked/")
def add_payment_to_sale(request, object_id): # AJAX POST ONLY
    obj = get_object_or_404(Sale, pk=object_id)
    doc=Transaction.objects.filter(doc_number=obj.doc_number)
    total=0
    for transaction in doc:
        for entry in transaction.entry_set.filter(account=obj.client):
            if entry.active: total+=entry.value
    payment=ClientPayment(doc_number=obj.doc_number, date=obj.date, source=obj.client, dest=PAYMENTS_RECEIVED_ACCOUNT, value=total)
    payment.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[payment],'prefix':'clientpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})
######################################################################################
# Accounting Views
######################################################################################
@login_required
@permission_required('inventory.change_accounting', login_url="/blocked/")
def edit_accounting(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Accounting, AccountingForm, "accounting")
    
@login_required
@permission_required('inventory.view_accounting', login_url="/blocked/")
def list_accounting(request, errors={}): # GET ONLY
    return search_and_paginate_transactions(request, Accounting,'inventory/accounting_list.html', errors)
@login_required
@permission_required('inventory.change_accounting', login_url="/blocked/")
def new_accounting(request): # AJAX POST ONLY
    error_list={}
    # get the doc number
    try: doc_number=request.POST['doc_number']
    except: doc_number='' 
    if doc_number=='': doc_number=Accounting.objects.next_doc_number()
    # get the date
    try: 
        sample=Accounting.objects.filter(doc_number=doc_number)[0]
        date=sample.date
    except:
        date=datetime.now()
    if len(error_list)==0:
        transaction=Accounting(
            doc_number=doc_number, 
            date=date, 
            debit_account=DEFAULT_ACCOUNTING_DEBIT_ACCOUNT, 
            credit_account=DEFAULT_ACCOUNTING_CREDIT_ACCOUNT)
        transaction.save()
        objects=[transaction]
    else:
        objects=[]
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':objects,'prefix':'accounting','line_template':"inventory/accounting.html",'error_list':error_list, 'info_list':{}})
    
def delete_accounting(request, object_id):
    return delete_object(request, object_id, Accounting, 'accounting')    
######################################################################################
# Return Views
######################################################################################
@login_required
@permission_required('inventory.change_salereturn', login_url="/blocked/")
def edit_salereturn(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, SaleReturn, SaleForm, "salereturn")
    
@login_required
@permission_required('inventory.change_salereturn', login_url="/blocked/")
def new_salereturn(request, object_id): # AJAX POST ONLY
    sale = get_object_or_404(Sale, pk=object_id)
    
    salereturn=SaleReturn(
        doc_number=sale.doc_number,
        date=sale.date,
        client=sale.client,
        item=sale.item,
        quantity=-sale.quantity,
        serial=sale.serial,
        price=-sale.price,
        cost=-sale.cost,
        tax=-sale.tax,
        discount=-sale.discount,
    )
    salereturn.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[salereturn],'prefix':'salereturn','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.delete_salereturn', login_url="/blocked/")
def delete_salereturn(request, object_id):
    return delete_object(request, object_id, Sale, 'sale')
########################################################################################
@login_required
@permission_required('inventory.change_purchasereturn', login_url="/blocked/")
def edit_purchasereturn(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, PurchaseReturn, PurchaseForm, "purchasereturn")
    
@login_required
@permission_required('inventory.change_purchasereturn', login_url="/blocked/")
def new_purchasereturn(request, object_id): # AJAX POST ONLY
    purchase = get_object_or_404(Purchase, pk=object_id)
    
    purchasereturn=PurchaseReturn(
        doc_number=purchase.doc_number, 
        date=purchase.date, 
        cost=-purchase.cost,
        item=purchase.item, 
        quantity=-purchase.quantity, 
        serial=purchase.serial,
        vendor=purchase.vendor, 
    )
    purchasereturn.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[purchasereturn],'prefix':'purchasereturn','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.delete_purchasereturn', login_url="/blocked/")
def delete_purchasereturn(request, object_id):
    return delete_object(request, object_id, PurchaseReturn, 'purchasereturn')
######################################################################################
# Refunds
######################################################################################

@login_required
@permission_required('inventory.change_clientrefund', login_url="/blocked/")
def edit_clientrefund(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, ClientRefund, ClientPaymentForm, "clientrefund")
    
@login_required
@permission_required('inventory.change_clientrefund', login_url="/blocked/")
def new_clientrefund(request, object_id): # AJAX POST ONLY
    payment = get_object_or_404(ClientPayment, pk=object_id)
    
    refund=ClientRefund(
        doc_number=payment.doc_number, 
        date=payment.date, 
        value=-payment.value,
        source=payment.source,  
    )
    refund.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[refund],'prefix':'clientrefund','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.delete_clientrefund', login_url="/blocked/")
def delete_clientrefund(request, object_id):
    return delete_object(request, object_id, ClientRefund, 'clientrefund')
######################################################################################
# Vendor Refunds
######################################################################################
@login_required
@permission_required('inventory.change_vendorrefund', login_url="/blocked/")
def edit_vendorrefund(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, VendorRefund, VendorPaymentForm, "vendorrefund")
    
@login_required
@permission_required('inventory.change_vendorrefund', login_url="/blocked/")
def new_vendorrefund(request, object_id): # AJAX POST ONLY
    payment = get_object_or_404(VendorPayment, pk=object_id)
    
    refund=VendorRefund(
        doc_number=payment.doc_number, 
        date=payment.date, 
        value=-payment.value,
        dest=payment.dest,  
    )
    refund.save()
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[refund],'prefix':'vendorrefund','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})

@login_required
@permission_required('inventory.delete_vendorrefund', login_url="/blocked/")
def delete_vendorrefund(request, object_id):
    return delete_object(request, object_id, VendorRefund, 'vendorrefund')
######################################################################################
# Payment Views
######################################################################################
# Client Payments
######################################################################################
@login_required
@permission_required('inventory.change_clientpayment', login_url="/blocked/")
def edit_clientpayment(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, ClientPayment, ClientPaymentForm, "clientpayment")
    
@login_required
@permission_required('inventory.change_clientpayment', login_url="/blocked/")
def new_clientpayment(request): # AJAX POST ONLY
    try: doc_number=request.POST['doc_number']
    except: doc_number='7777' # TODO This should grab the next available doc_number
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
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[clientpayment],'prefix':'clientpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})
    
def delete_clientpayment(request, object_id):
    return delete_object(request, object_id, ClientPayment, 'clientpayment')
######################################################################################
# Vendor Payments
######################################################################################
@login_required
@permission_required('inventory.change_vendorpayment', login_url="/blocked/")
def edit_vendorpayment(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, VendorPayment, VendorPaymentForm, "vendorpayment")
    
@login_required
@permission_required('inventory.change_vendorpayment', login_url="/blocked/")
def new_vendorpayment(request): # AJAX POST ONLY
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
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[vendorpayment],'prefix':'vendorpayment','line_template':"inventory/transaction.html",'error_list':{}, 'info_list':{}})
    
def delete_vendorpayment(request, object_id):
    return delete_object(request, object_id, VendorPayment, 'vendorpayment')
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
def delete_transaction(request, object_id):
    return delete_object(request, object_id, Transaction, 'transaction')
def mark_transaction(request, object_id, attr, value):
    obj = get_object_or_404(Transaction, pk=object_id).subclass
    if not request.user.has_perm('inventory.change_sale') and obj.tipo=='Sale': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_purchase') and obj.tipo=='Purchase': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_count') and obj.tipo=='Count': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_process') and obj.tipo=='Process': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_production') and obj.tipo=='Production': return http.HttpResponseRedirect("/blocked/")
    if not request.user.has_perm('inventory.change_productionorder') and obj.tipo=='ProductionOrder': return http.HttpResponseRedirect("/blocked/")
    if obj.tipo=='Process' and attr in ['delivered','active' ]:
        return _r2r(request,'inventory/results.html', {'objects':[obj],'error_list':{'Process':[_('Cannot be marked delivered or active'),]}, 'info_list':[]})
    if obj.tipo=='Job':
        if attr in ['delivered','active' ] and obj.quantity < 0 and not request.user.has_perm('production.start_production'):
            return _r2r(request,'inventory/results.html', {'objects':[obj],'error_list':{'Process':[_('You do not have sufficient rights to start production'),]}, 'info_list':[]})
        if attr in ['delivered','active' ] and obj.quantity > 0 and not request.user.has_perm('production.finish_production'):
            return _r2r(request,'inventory/results.html', {'objects':[obj],'error_list':{'Process':[_('You do not have sufficient rights to finish production'),]}, 'info_list':[]})
    setattr(obj, attr, value)
#    print "obj = " + str(obj)
#    print "obj.pk = " + str(obj.pk)
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
    try:report=Report.objects.get(name=settings.MOVEMENTS_REPORT_NAME)
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
#        request.GET['q']=doc_number
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (settings.MOVEMENTS_REPORT_NAME,))]}
        return list_sales(request, errors=errors)
    return render_string_to_pdf(Template(report.body), {'transactions':transactions, 'user':request.user})  
   
class Document():
    def __init__(self, number):
        self._price = None
        self._due = None
        self._client = None
        self._paid_on_spot = None
        self.transactions=Transaction.objects.filter(doc_number=number)
    def _get_number(self):
        return self.transactions[0].doc_number
    number=property(_get_number)
    def __getitem__(self, index):
        return self.transactions[index]
    def __repr__(self):
        return self.number
    def _get_price(self):
        if not self._price:
            self._price = Entry.objects.filter(transaction__doc_number=self.number, tipo='Revenue').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        return -self._price
    price=property(_get_price)
    value=property(_get_price)
    def _get_due(self):
        if not self._due:
#            self._due = Entry.objects.filter(transaction__doc_number=self.number, tipo='Client').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
            self._due = Entry.objects.filter(transaction__doc_number=self.number, date=self.transactions[0]._date, account=self.client, tipo='Debit').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        return self._due
    due=property(_get_due)
    def _get_paid_on_spot(self):
        if not self._paid_on_spot:
            self._paid_on_spot = Entry.objects.filter(transaction__doc_number=self.number, date=self.transactions[0]._date, account=self.client, tipo='Credit').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        return self._paid_on_spot
    paid_on_spot=property(_get_paid_on_spot)
    def _get_unpaid_on_spot(self):
        if not self._unpaid_on_spot:
            self._unpaid_on_spot = Entry.objects.filter(transaction__doc_number=self.number, date=self.transactions[0]._date, account=self.client).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        return self._unpaid_on_spot
    unpaid_on_spot=property(_get_unpaid_on_spot)
    def _get_client(self):
        if not self._client:
            self._client = Entry.objects.filter(transaction__doc_number=self.number, tipo='Client')[0].account
        return self._client
    client=property(_get_client)
        
def update_dict_list(x, y):
    for k in y.keys():
        if k in x:
            x[k].append(y[k])
        else:
            x[k]=[y[k]]
            
def create_documents(trans):
    d={}
    for t in trans:
        update_dict_list(d, {t.doc_number:t})
    documents=[]
    for doc in d:
        documents.append(Document(doc))
    return documents
def create_documents_from_entries(entries):
    d={}
    for e in entries:
        update_dict_list(d, {e.transaction.doc_number:e.transaction})
    documents=[]
    for doc in d:
        documents.append(Document(doc))
    return documents
    
class Series():
    def __init__(self, documents):
        self.documents=documents
    def append(self, document):
        self.documents.append(document)
    def __getitem__(self, index):
        return self.documents[index]    
    def __repr__(self):
        return str(self.documents)
    def __unicode__(self):
        if self.documents[0].number==self.documents[-1].number: return self.documents[0].number
        else: return "%s - %s" % (self.documents[0].number, self.documents[-1].number)
    def _get_first(self):
        return self.documents[0]
    first=property(_get_first)
    def _get_last(self):
        return self.documents[-1]
    last=property(_get_last)
    def _get_value(self):
        total=0
        for d in self.documents:
            total+=d.price
        return total
    value=property(_get_value)
        
        
def create_series(documents):
    from operator import attrgetter
    documents.sort(key=attrgetter('number'))
    series=[]
    last=0
    price=0
    for doc in documents:
        if series==[]:
            series.append(Series([doc]))
            l=re.split("(\d*)", doc.number)
            if len(l)>1:
                prefix=l[0:-2]
                last=int(l[-2])
            else:
                prefix=''
                last=0
        else:
            x=int(re.split("(\d*)", doc.number)[-2])
            if x-1==last or x==last: series[-1].append(doc)
            else: series.append(Series([doc]))
            last=x
    return series
    
def separate_by_paid_on_spot(documents):
    paid= []
    unpaid=[]
    for doc in documents:
        print "doc.number = " + str(doc.number)
        print "doc.paid_on_spot = " + str(doc.paid_on_spot)
        print "doc.due = " + str(doc.due)
        print "doc.paid_on_spot==doc.due = " + str(doc.paid_on_spot==doc.due)
        if doc.paid_on_spot==doc.due: 
            print "adding to paid"
            paid.append(doc)
        else: 
            print "adding to unpaid"
            unpaid.append(doc)
    print "paid = " + str(paid)
    print "unpaid = " + str(unpaid)
    return (paid, unpaid)
    
def separate_payments_by_timing(payments):
    groups={'Early':[], 'OnTime':[],'Late':[],'Down':[],'Over':[]}
    for payment in payments: update_dict_list(groups, {payment.timing:payment})
    return groups
    
def separate_by_tax_group(documents):
    groups={}
    for doc in documents: update_dict_list(groups, {doc.client.tax_group.name:doc})
    return groups.values()
#class SeriesCollection():
#    def __init__(self, documents):
#        
#    def __getitem__(self, index):
#        return self.series[index]
#    def __repr__(self):
#        return repr(str(self.series))
        
#def group_trans_by_doc_number(trans):
#    d={}
#    for t in trans:
#        update_dict_list(d, {t.doc_number:t})
#    return d

#def group_docs(docs):
#    result=[]
#    last=0
#    price=0
#    for doc in docs:
#        if result==[]:
#            result.append([doc])
#            l=re.split("(\d*)", doc[0].doc_number)
#            prefix=l[0:-2]
#            last=int(l[-2])
#        else:
#            x=int(re.split("(\d*)", doc[0].doc_number)[-2])
#            if x-1==last or x==last: result[-1].append(doc)
#            else: result.append([doc])
#            last=x
#    return result
            
@login_required
@permission_required('inventory.view_sale', login_url="/blocked/")
def corte(request):
    form=SearchForm(request.GET)
    form.is_valid()
    start=form.cleaned_data['start']
    end=form.cleaned_data['end']
    sales = Sale.objects.all().order_by('doc_number')
    print "REVENUE_ACCOUNT = " + str(REVENUE_ACCOUNT)
    sale_entries = Entry.objects.filter(tipo='Revenue')
    print "sale_entries.count() = " + str(sale_entries.count())
    payments = ClientPayment.objects.all().order_by('-_date')
    cash = Entry.objects.filter(account=CASH_ACCOUNT)
    revenue = Entry.objects.filter(account__number__startswith=REVENUE_ACCOUNT.number)
    expense = Entry.objects.filter(account=EXPENSE_ACCOUNT)
    tax = Entry.objects.filter(account__number__startswith=TAX_ACCOUNT.number)
    if not start and not end:
        from datetime import datetime
        start=datetime.date(datetime.now())
        end=start+timedelta(days=1)
    if start:
        sales=sales.filter(_date__gte=start)
        sale_entries=sale_entries.filter(transaction___date__gte=start)
        print "sale_entries.count() = " + str(sale_entries.count())
        payments=payments.filter(_date__gte=start)
        cash=cash.filter(date__gte=start)
        revenue=revenue.filter(date__gte=start)
        expense=expense.filter(date__gte=start)
        tax=tax.filter(date__gte=start)
        initial_cash=Entry.objects.filter(account=CASH_ACCOUNT, date__lt=start).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    else:
        initial_cash=Entry.objects.filter(account=CASH_ACCOUNT, date__lte=datetime.date(datetime.now())).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    if end:
        deadline = end + timedelta(days=1)
        sales=sales.filter(_date__lt=deadline)
        sale_entries=sale_entries.filter(transaction___date__lt=deadline)
        print "sale_entries.count() = " + str(sale_entries.count())
        payments=payments.filter(_date__lt=deadline)
        cash=cash.filter(date__lt=deadline)
        revenue=revenue.filter(date__lt=deadline)
        expense=expense.filter(date__lt=deadline)
        tax=tax.filter(date__lt=deadline)
        
    # Organize sales:
    # if it was made and paid today, group by tax_group
    # otherwise put it in the "unpaid" list
#    sales_docs=create_documents(sales)
    sales_docs=create_documents_from_entries(sale_entries)
    paid_sales, unpaid_sales = separate_by_paid_on_spot(sales_docs)
    print "paid_sales = " + str(paid_sales)
    print "unpaid_sales = " + str(unpaid_sales)
    # put each paid doc in a list for its tax_group
    tax_groups = separate_by_tax_group(paid_sales)
    
    # group the documents into series
    tax_groups_by_series=[]
    for group in tax_groups:
        tax_groups_by_series.append(create_series(group))
        
    # group payments by timing
    # returns a dict with three lists of payments: 'Early', 'OnTime', and 'Late'
    grouped_payments=separate_payments_by_timing(payments)
        
    try:report=Report.objects.get(name=settings.CORTE_REPORT_NAME)
    except Report.DoesNotExist: 
        request.GET=request.GET.copy()
        errors={'Report':[unicode(_('Unable to find a report template with the name "%s"') % (settings.CORTE_REPORT_NAME,))]}
        return item_list(request, errors=errors)
    cash=cash.aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    revenue=-revenue.aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    expense=expense.aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    tax=-tax.aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    return render_string_to_pdf(Template(report.body), {
        'start':start or datetime.now(),
        'end':end,
        'tax_groups':tax_groups,
        'sales':sale_entries,
        'payments':payments,
        'paid_sales':paid_sales,
        'unpaid_sales':unpaid_sales,
        'tax_groups_by_series':tax_groups_by_series,
        'grouped_payments':grouped_payments,
        'user':request.user,
        'settings.COMPANY_NAME':settings.COMPANY_NAME,
        'cash':cash,
        'revenue':revenue,
        'earnings':cash-initial_cash-expense-tax,
        'expense':expense,
        'tax':tax,
        'final_cash':CASH_ACCOUNT.balance,
        'initial_cash':initial_cash
    })  
    
######################################################################################
# Transfer Views
######################################################################################
@login_required
@permission_required('inventory.view_transfer', login_url="/blocked/")
def list_transfers(request): # GET ONLY
    return search_and_paginate_transactions(request, Transfer,'inventory/transfers.html')

@login_required
@permission_required('inventory.change_transfer', login_url="/blocked/")
def edit_transfer(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Transfer, TransferForm, "transfer")

@login_required
@permission_required('inventory.change_transfer', login_url="/blocked/")
def new_transfer(request): # AJAX POST ONLY
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
    return _r2r(request,'inventory/results.html', {'edit_mode':True, 'objects':[transfer],'prefix':'transfer','line_template':"inventory/transaction.html",'error_list':error_list, 'info_list':{}})

def delete_transfer(request, object_id):
    return delete_object(request, object_id, Transfer, 'transfer')
