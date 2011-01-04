from django.db import models

#class Repository(models.Model):
#    name = models.CharField('name', max_length=32)
#    def __unicode__(self):
#        return self.name
#    def pull(self):
#        result=subprocess.call('git pull',shell=True)
#        
#        
#class DbUpdate(models.Model):
#    name = models.CharField('name', max_length=32)
#    sql = models.CharField('sql', max_length=32)
#    
#def update_all():
#    from django.db import connection, transaction
#    cursor = connection.cursor()

#    for k,v in updates.items():
#        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
#        row = cursor.fetchone()
class UpdatesRun(models.Model):
    name = models.CharField('name', max_length=32)
    def __unicode__(self):
        return "Update:" + self.name

def run_updates():
    from jade.updates import db_updates
    import jade
    updates_applied=[]
    print "dir(db_updates) = " + str(dir(db_updates))
    for update in dir(db_updates):
        if not (update=='Update' or update[0]=='_'):
            try: UpdatesRun.objects.get(name=update)
            except UpdatesRun.DoesNotExist:
                jade.inventory.models.Count
                error=eval("jade.updates.db_updates." + update)()()
                if not error:
                    UpdatesRun.objects.create(name=update)
                    updates_applied.append(update)
    return updates_applied
            
class Update(object):
    def __call__(self):
        raise NotImplemented()
