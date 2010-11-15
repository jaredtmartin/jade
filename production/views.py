from jade.production.models import Process, Job, Production
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import permission_required, login_required
from jade.inventory.views import search_and_paginate_transactions, search_transactions, paginate_transactions, _r2r, edit_object, search_entries
from jade.production.forms import NewProcessForm, ProcessForm, JobForm
from jade.inventory.forms import SearchForm
from django import http
from jade.inventory.models import Entry


@login_required
@permission_required('production.view_process', login_url="/blocked/")
def process_list(request): # GET ONLY
    return search_and_paginate_transactions(request, Process,'production/process_list.html', strict=False)
    
@login_required
@permission_required('production.view_job', login_url="/blocked/")
def job_list(request): # GET ONLY
    return search_and_paginate_transactions(request, Job,'production/job_list.html')
    
@login_required
@permission_required('production.view_production', login_url="/blocked/")
def production_list(request): # GET ONLY
    return search_and_paginate_transactions(request, Production,'production/production_list.html', strict=False)
    
@login_required
@permission_required('production.create_process', login_url="/blocked/")
def process_new(request): # POST ONLY
    form=NewProcessForm(request.POST)
    if form.is_valid():
        process=form.save()
        info_list=[_('The process has been created.')]
    else:
        process=None
        info_list=[]
    error_list=form.errors
    return _r2r(request,'inventory/results.html', {'edit_mode':True,'objects':[process], 'error_list':{}, 'info_list':info_list})
    
@login_required
@permission_required('production.change_process', login_url="/blocked/")
def process_edit(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Process, ProcessForm, "process")
    
@login_required
@permission_required('production.delete_process', login_url="/blocked/")
def process_delete(request, object_id):
    return delete_object(request, object_id, Process, 'process')
    
@login_required
@permission_required('production.create_job', login_url="/blocked/")
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
        try: jobs.append(process.transaction.subclass.plan(new_number, times, cost=item_cost*process.quantity*-1))
        except AttributeError: pass
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
@permission_required('production.delete_job', login_url="/blocked/")
def job_delete(request, object_id):
    return delete_object(request, object_id, Job, 'job')
    
@login_required
@permission_required('production.start_production', login_url="/blocked/")
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
@permission_required('production.finish_production', login_url="/blocked/")
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
@permission_required('production.change_job', login_url="/blocked/")
def job_edit(request, object_id): # AJAX POST ONLY
    return edit_object(request, object_id, Job, JobForm, "job")
