from django import template
import locale
register = template.Library()

@register.filter
def running_total(items,attr):
    #events_sum=sum(d.category.active_products.0.unit_price for d in items)
    events_sum=0
    if items:
        for d in items:
            events_sum+=getattr(d,attr)
            #elif items.category:
               # events_sum="e"
            #categories_sum=sum(d.event.product.unit_price for d in items)
    return events_sum

#pack_total.is_safe = True
running_total.is_safe = True


@register.filter
def currency(value,mxn=False):
    try:
        locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL,'')
    loc = locale.localeconv()
    currency=locale.currency(value, loc['currency_symbol'], grouping=True)
    if mxn:
    	return currency+" MXN"
    else:
    	return currency+" USD"

currency.is_safe = True

# @register.filter
# def asientos_add(asientos):
#     for asiento in asientos:
#         if asiento.seccion="1":
#             return "true"
#         else: 
#             return "false"