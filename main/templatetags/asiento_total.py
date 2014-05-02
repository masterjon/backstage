from django import template
register = template.Library()


@register.filter
def seat_count(items, argstr):
    #events_sum=sum(d.category.active_products.0.unit_price for d in items)
    args = argstr.split(",")
    seccion = args[0] if len(args) >= 1 else ""
    tipo = args[1] if len(args) >= 2 else ""
    events_sum = 0
    for d in items:
        if d.seccion == seccion and d.tipo == tipo:
            events_sum += 1
    return events_sum


#pack_total.is_safe = True
seat_count.is_safe = True


@register.filter
def orden_seat_count(items, argstr):
    args = argstr.split(",")
    seccion = args[0] if len(args) >= 1 else ""
    tipo = args[1] if len(args) >= 2 else ""
    events_sum = 0
    for orden in items:
        for orden_asiento in orden.ordenasiento_set.all():
            if orden_asiento.seccion == seccion and orden_asiento.tipo == tipo:
                events_sum += 1
    return events_sum

orden_seat_count.is_safe = True
