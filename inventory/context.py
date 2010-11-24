from django.conf import settings

def company_name(request):
    return {
        'company_name': settings.COMPANY_NAME,
        'date_format': settings.DATE_FORMAT,
    }
