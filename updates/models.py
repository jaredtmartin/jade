from django.db import models

class Repository(models.Model):
    name = models.CharField('name', max_length=32)
    def __unicode__(self):
        return self.name
    def pull(self):
        result=subprocess.call('git pull',shell=True)
        
        
class DbUpdate(models.Model):
    name = models.CharField('name', max_length=32)
    sql = models.CharField('sql', max_length=32)
    
def update_all():
    from django.db import connection, transaction
    cursor = connection.cursor()

    for k,v in updates.items():
        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
        row = cursor.fetchone()
