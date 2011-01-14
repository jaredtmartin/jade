from jade.inventory.views import _r2r
from jade.updates.models import run_updates
from django.contrib.auth.decorators import permission_required, login_required
@login_required
@permission_required('impossible', login_url="/blocked/")
def pull(request):
    import commands
    updates_applied=[]
    try: command='cd %s;git pull %s' % (settings.APP_LOCATION, Setting.get('Git repo'))
    except: command='git pull origin master'
    results = commands.getstatusoutput(command) 
    d=commands.getstatusoutput('') 
    updates_applied=run_updates()
    if not results[0]: # No errors fetching
        updates_applied=run_updates()
    return _r2r(request,'updates/pull.html', {'error':results[0],'msg':results[1], 'updates_applied':updates_applied})
    
