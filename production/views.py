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
from jade.production.models import Process, Job, Production
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import permission_required, login_required
from jade.inventory.views import render_string_to_pdf, search_and_paginate_transactions, search_transactions, paginate_transactions, _r2r, edit_object, search_entries
from jade.production.forms import NewProcessForm, ProcessForm, JobForm
from jade.inventory.forms import SearchForm
from django import http
from jade.inventory.models import Report, Entry
from django.template import Template, Context, RequestContext
import settings


@login_required
@permission_required('inventory.view_process', login_url="/blocked/")
def process_list(request): # GET ONLY
    return search_and_paginate_transactions(request, Process,'production/process_list.html', strict=False)
    
@login_required
@permission_required('inventory.view_job', login_url="/blocked/")
def job_list(request): # GET ONLY
    return search_and_paginate_transactions(request, Job,'production/job_list.html')
    
@login_required
@permission_required('inventory.view_production', login_url="/blocked/")
def production_list(request): # GET ONLY
    return search_and_paginate_transactions(request, Production,'production/production_list.html', strict=False)

@login_required
@permission_required('inventory.view_job', login_url="/blocked/")
def job_report(request, doc_number):
    doc=Job.objects.filter(doc_number=doc_number)
    if doc.count()==0: return fallback_to_transactions(request, doc_number, _('Unable to find job with the specified document number.'))
    try:report=Report.objects.get(name=settings.JOB_REPORT_NAME)
    except Report.DoesNotExist: 
        return fallback_to_transactions(request, doc_number, _('Unable to find a report template with the name "%s"') % settings.GARANTEE_REPORT_NAME)
    production=[]
    consumption =[]   
    for l in doc:    
        if l.quantity>=0: production.append(l)
        else: consumption.append(l)
    
    return render_string_to_pdf(Template(report.body), {'doc':doc,'consumption':consumption, 'production':production})
@login_required
@permission_required('inventory.view_job', login_url="/blocked/")
def process_report(request, doc_number):
    doc=Process.objects.filter(doc_number=doc_number)
    if doc.count()==0: return fallback_to_transactions(request, doc_number, _('Unable to find process with the specified document number.'))
    try:report=Report.objects.get(name=settings.PROCESS_REPORT_NAME)
    except Report.DoesNotExist: 
        return fallback_to_transactions(request, doc_number, _('Unable to find a report template with the name "%s"') % settings.GARANTEE_REPORT_NAME)
    production=[]
    consumption =[]   
    for l in doc:    
        if l.quantity>=0: production.append(l)
        else: consumption.append(l)
    return render_string_to_pdf(Template(report.body), {'doc':doc,'consumption':consumption, 'production':production})


@login_required
@permission_required('inventory.add_process', login_url="/blocked/")
def process_new(request): # POST ONLY
    form=NewProcessForm(request.POST)
    if form.is_valid():
        process=form.save()
        print "process = " + str(process)
        print "process.pk = " + str(process.pk)
        print "process.template = " + str(process.template)
        process.edit_mode=True
        
        info_list=[_('The process has been created.')]
    else:
        process=None
        info_list=[]
    error_list=form.errors
    return _r2r(request,'inventory/results.html', {'edit_mode':True,'objects':[process], 'error_list':{}, 'info_list':info_list})
    
@login_required
@permission_required('inventory.change_process', login_url="/blocked/")
def process_edit(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Process, ProcessForm, "process")
    
@login_required
@permission_required('inventory.delete_process', login_url="/blocked/")
def process_delete(request, object_id):
    return delete_object(request, object_id, Process, 'process')
    
@login_required
@permission_required('inventory.add_job', login_url="/blocked/")
def job_new(request):
    form=SearchForm(request.GET, validate=True)
    try: times=int(request.GET['quantity'])
    except: times=1
    q=form.cleaned_data['q']
    start=form.cleaned_data['start']
    end=form.cleaned_data['end']
    entries=search_entries(request.user, form, 'Production').filter(transaction__tipo='Process')
    print str([type(x.transaction.subclass) for x in entries])
    if  entries.count()>0: new_number=entries[0].transaction.subclass.next_doc_number()
    else: new_number=''
    total_cost=total_prod=0
    jobs=[]
    # First do consumptions
    for process in entries.filter(quantity__gt=0):
#        print "id:%i, item:%s, qty:%i, val:%i, acct:%s, tipo:%s" % (x.pk, x.item, x.quantity, x.value, x.account.name, x.tipo)
        item_cost=process.item.cost
        total_cost += item_cost * process.quantity
        jobs.append(process.transaction.subclass.plan(new_number, times, cost=item_cost*process.quantity*-1))
#        except AttributeError: pass
#        print "item_cost = " + str(item_cost)
#        print "total_cost = " + str(total_cost)
    # Now do productions
    for process in entries.filter(quantity__lt=0):
#        print "process.value = " + str(process.value)
#        print "process.quantity = " + str(process.quantity)
#        print "process.value * process.quantity = " + str(process.value * process.quantity)
        total_prod += process.value * process.quantity
#        print "total_prod = " + str(total_prod)
    for process in entries.filter(quantity__lt=0):
#        print "process.item.name = " + str(process.item.name)
#        print "process.value = " + str(process.value)
#        print "total_prod = " + str(total_prod)
#        print "total_cost = " + str(total_cost)
#        print "process.value/total_prod = " + str(process.value/total_prod)
#        print "process.value/total_prod*total_cost = " + str(process.value/total_prod*total_cost)
        cost=process.value/total_prod*total_cost*-1
        try: jobs.append(process.transaction.subclass.plan(new_number, times, cost=cost))
        except AttributeError: pass
    return http.HttpResponseRedirect('/production/job/list/?q=%s' % new_number)
    
@login_required
@permission_required('inventory.delete_job', login_url="/blocked/")
def job_delete(request, object_id):
    return delete_object(request, object_id, Job, 'job')
    
@login_required
@permission_required('inventory.start_production', login_url="/blocked/")
def job_start(request):
    form=SearchForm(request.GET, validate=True)
    q=form.cleaned_data['q']
    start=form.cleaned_data['start']
    end=form.cleaned_data['end']
    jobs=search_transactions(request.user,form, Job.objects.all())
    print "jobs.count() = " + str(jobs.count())
    for job in jobs:
        print "job.quantity = " + str(job.quantity)
        if job.quantity<0:
            print "setting"
            job.active=True
            job.delivered=True
            job.save()
    return http.HttpResponseRedirect('/production/job/list/?q=%s' % q)
    
@login_required
@permission_required('inventory.finish_production', login_url="/blocked/")
def job_finish(request):
    form=SearchForm(request.GET, validate=True)
    q=form.cleaned_data['q']
    start=form.cleaned_data['start']
    end=form.cleaned_data['end']
    jobs=search_transactions(request.user,form, Job.objects.all())
    for job in jobs:
        if job.quantity>0:
            job.active=True
            job.delivered=True
            job.save()
    return http.HttpResponseRedirect('/production/job/list/?q=%s' % q)
    
@login_required
@permission_required('inventory.change_job', login_url="/blocked/")
def job_edit(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Job, JobForm, "job")
