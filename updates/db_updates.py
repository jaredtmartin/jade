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
class DeliverbyDefaultSetting(Update):
    """Adds this setting to the database"""
    def __call__(self):
        from jade.inventory.models import Setting
        Setting.objects.create(name='Deliver by default', value=True)
        
class AddAccounting(Update):
    """Adds this setting to the database"""
    def __call__(self):
        from jade.inventory.models import *
        a=Account.objects.create(name='Empleados', number='0203', multiplier=-1)
        TransactionTipo.objects.create(name='Expense', obj='jade.inventory.models.Expense')
        TransactionTipo.objects.create(name='EmployeePay', obj='jade.inventory.models.EmployeePay')
        Setting.objects.create(name='Employees account', value=a)
        
class AddWork(Update):
    """Adds this setting to the database"""
    def __call__(self):
        from jade.inventory.models import TransactionTipo
        TransactionTipo.objects.create(name='Work', obj='jade.inventory.models.Work')
        
class AddTransferAccountSetting(Update):
    """Adds this setting to the database"""
    def __call__(self):
        from jade.inventory.models import Account, Setting
        a=Account.objects.get(name='Gastos de Transferencias')
        Setting.objects.create(name='Transfer account', value=a)
        
class CashAccountSetting(Update):
    """Adds this setting to the database if it does not already exist"""
    def __call__(self):
        from jade.inventory.models import Account, Setting
        try: a=Account.objects.get(name='Starting cash account balance')
        except Account.DoesNotExist: Setting.objects.create(name='Starting cash account balance', value=25)

class CorteReportSetting(Update):
    """Adds this setting to the database if it does not already exist"""
    def __call__(self):
        from jade.inventory.models import Report, Setting
        
        try: a=Setting.objects.get(name='Cash closing report')
        except Setting.DoesNotExist: 
            r=Report.objects.get(name='Corte de Caja')
            Setting.objects.create(name='Cash closing report', value=r)

class GaranteeReportSettings(Update):
    """Adds this setting to the database if it does not already exist"""
    def __call__(self):
        from jade.inventory.models import Report, Setting
        try: a=Report.objects.get(name='Reporte de Garantias')
        except Report.DoesNotExist: a=Report.objects.create(name='Reporte de Garantias', body="""
        <html>
    <head>
        <title></title>
        <meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1" >
        <meta http-equiv="Content-Script-Type" content="text/javascript" >
        <meta http-equiv="Content-Style-Type" content="text/css" >
        <style type="text/css">
            h1 {
                height: 60px;
                min-width: 960px;
                background: #e4f2fd;
                border-bottom: 1px solid #c6d9e9;
                font-family:Georgia,Times,"Times New Roman",serif;
                font-weight:normal;
                color:#555555;
                font-size:36px;
                line-height:1em;
                min-width:500px;
                padding-top:34px;
                text-align:center;
                text-shadow:0 1px 0 #E4F2FD;
            }
            th{text-align:left;}
            .row1{  
                -moz-background-clip:border;
                -moz-background-inline-policy:continuous;
                -moz-background-origin:padding;
                background:#EDF3FE none repeat scroll 0 0;
            }
            .row2{
                -moz-background-clip:border;
                -moz-background-inline-policy:continuous;
                -moz-background-origin:padding;
                background:white none repeat scroll 0 0;
            }
            body{line-height:16px;}
            td.numero {text-align:left;}
            td.texto {text-align:left;}
            table {border:solid;height:200px;}
            @page {
                size:letter;
                {% if watermark_filename %}
                    background-image: url({{watermark_filename}});
                {% endif %}
                top: 1cm;
                left: 1cm;
                right: 1.7cm;
                @frame footer{
                    bottom:2cm;
                    height:5cm;
                    left: 3cm;
                    right: 3cm;
                    -pdf-frame-content: footerContent;
                }
            }
        </style>
    </head>
    <body>
<h1>{{company_name}}          {{ doc.0.doc_number }}</h1>
<p>Este Documento contiene la lista de numeros de serie de su compra.</p>
        <table id="tableContent">
            <thead>
                <tr><th>Fecha</th><th>Producto</th><th>Numero de Serie</th><th>Vence</th></tr>
            </thead>
            <tbody>
                {% for garantee in doc %}
                    <tr class="{% cycle "row1" "row2" %}">
                        <td class="texto" >{{garantee.date|date:"d/m/Y"}}</td>
                        <td class="texto" >{{garantee.item.name}}</td>
                        <td class="numero" >{{garantee.serial}}</td>
                        <td class="numero" >{{garantee.expires|date:"d/m/Y"}}</td>
                    </tr>
                {%endfor%}
            </tbody>            
        </table>
<div id="footerContent">
<h3>Notas para hacer efectiva la Garantia</h3>
<ul>
<li>Este documento es necesario para hacer efectiva la garantia asi como los acesorios y las cajas</li>
<li>Si el producto presenta dano físico como magulladura, rupturas, o corrosion la garantía podra no ser ortorgada.</li>
<li>Si los numeros de serie presenta, tachadura, borrones, rayones, odesgaste, en el producto podria no otorgarse la garantia.</li>
<li>El servicio de garantia a domocilio esta sujeto a cobros extra.</li>
</ul>
</div>
    </body>
</html> """)
        try: s=Setting.objects.get(name='Reporte de Garantias')
        except Setting.DoesNotExist: Setting.objects.create(name='Reporte de Garantias', value=a)

