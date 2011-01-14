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
class AddSettingForBlockingSalesWithoutInventory(Update):
    def __call__(self):
        from jade.inventory.models import Setting
        Setting.objects.create(name='Allow sales without inventory', tipo="__builtin__.bool", value="True")
