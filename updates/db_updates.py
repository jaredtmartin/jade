from jade.updates.models import Update
# An update should inherit from Update, implement __call__ and return a list of errors or other messages if any.
class HelloWorld(Update):
    def __call__(self):
        print "Hello World"
        
class HelloAgain(Update):
    def __call__(self):
        print "Hello Again"

class ListItems(Update):
    def __call__(self):
        from jade.inventory.models import Item
        for i in Item.objects.all():
            print i
class AllowSalesWithoutInventory(Update):
    """Adds this setting to the database"""
    def __call__(self):
        from jade.inventory.models import Setting
        Setting.objects.create(name='Allow sales without inventory', tipo="__builtin__.bool", value="True")
class AddSettingsForLabels(Update):
    """Adds this setting to the database"""
    def __call__(self):
        from jade.inventory.models import Setting
        Setting.objects.create(name='Labels per line', tipo="__builtin__.int", value="4")
        Setting.objects.create(name='Labels per page', tipo="__builtin__.int", value="44")
class FixSettingForLabels(Update):
    """Adds this setting to the database"""
    def __call__(self):
        from jade.inventory.models import Setting
        s=Setting.objects.get(name='Labels per page')
        s.name='Lines per page'
        s.value=11
        s.save()
class SettingSalesWoInventory(Update):
    """Adds this setting to the database"""
    def __call__(self):
        from jade.inventory.models import Setting
        
        try: Setting.objects.delete(name='Labels per line')
        except:pass
        try: Setting.objects.delete(name='Labels per page')
        except:pass
        try: Setting.objects.delete(name='Lines per page')
        except:pass
        Setting.objects.create(name='Sales without inventory', value="limit")
        Setting.objects.create(name='Labels per line', value=4)
        Setting.objects.create(name='Lines per page', value=11)
