from django.contrib import admin
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from models import Show,slideHome,fotosGallery,Horario,Asiento,HorarioAsiento,Contacto,Orden,Artista,Vendedor,OrdenAsiento,video,FormaPago,TipoCambio,CustomText
class ButtonAdmin(admin.ModelAdmin):
    """
    A subclass of this admin will let you add buttons (like history) in the
    change view of an entry.

    ex.
    class FooAdmin(ButtonAdmin):
       ...

       def bar(self, request, obj=None):
          if obj != None: obj.bar()
          return None # Redirect or Response or None
       bar.short_description='Example button'

       list_buttons = [ bar ]
       change_buttons = [ bar ]

    you can then put the following in your admin/change_form.html template:

       {% block object-tools %}
           {% if change %}{% if not is_popup %}
           <ul class="object-tools">
           {% for button in buttons %}
             <li><a href="{{ button.func_name }}/">{{ button.short_description }}</a></li>
           {% endfor %}
           <li><a href="history/" class="historylink">History</a></li>
           {% if has_absolute_url %}<li><a href="../../../r/{{ content_type_id }}/{{ object_id }}/" class="viewsitelink">View on site</a></li>{% endif%}
           </ul>
           {% endif %}{% endif %}
       {% endblock %}

    """
    change_buttons=[]
    list_buttons=[]

    def button_view_dispatcher(self, request, url):
        # Dispatch the url to a function call
        if url is not None:
            import re
            res = re.match('(.*/)?(?P<id>\d+)/(?P<command>.*)', url)
            if res:
                if res.group('command') in [b.func_name for b in self.change_buttons]:
                    obj = self.model._default_manager.get(pk=res.group('id'))
                    response = getattr(self, res.group('command'))(request, obj)
                    if response is None:
                        from django.http import HttpResponseRedirect
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
                    return response
            else:
                res = re.match('(.*/)?(?P<command>.*)', url)
                if res:
                    if res.group('command') in [b.func_name for b in self.list_buttons]:
                        response = getattr(self, res.group('command'))(request)
                        if response is None:
                            from django.http import HttpResponseRedirect
                            return HttpResponseRedirect(request.META['HTTP_REFERER'])
                        return response
        # Delegate to the appropriate method, based on the URL.
        from django.contrib.admin.util import unquote
        if url is None:
            return self.changelist_view(request)
        elif url == "add":
            return self.add_view(request)
        elif url.endswith('/history'):
            return self.history_view(request, unquote(url[:-8]))
        elif url.endswith('/delete'):
            return self.delete_view(request, unquote(url[:-7]))
        else:
            return self.change_view(request, unquote(url))

    def get_urls(self):
        from django.conf.urls.defaults import url, patterns
        from django.utils.functional import update_wrapper
        # Define a wrapper view
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        #  Add the custom button url
        urlpatterns = patterns('',
            url(r'^(.+)/$', wrap(self.button_view_dispatcher),)
        )
        return urlpatterns + super(ButtonAdmin, self).get_urls()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not extra_context: extra_context = {}
        if hasattr(self, 'change_buttons'):
            extra_context['buttons'] = self._convert_buttons(self.change_buttons)
        if '/' in object_id:
            object_id = object_id[:object_id.find('/')]
        return super(ButtonAdmin, self).change_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        if not extra_context: extra_context = {}
        if hasattr(self, 'list_buttons'):
            extra_context['buttons'] = self._convert_buttons(self.list_buttons)
        return super(ButtonAdmin, self).changelist_view(request, extra_context)

    def _convert_buttons(self, orig_buttons):
        buttons = []
        for b in orig_buttons:
            buttons.append({ 'func_name': b.func_name, 'short_description': b.short_description })
        return buttons

class AsientoAdmin(admin.ModelAdmin):
	list_display = ('id','seccion', 'mesa', 'asiento')
	fields = ('seccion', 'mesa', 'asiento')
class VendedorAdmin(admin.ModelAdmin):
	list_display = ('nombre','canal', 'anticipo','comision')
	fields = ('nombre', 'canal','anticipo','comision')

class OrdenAsientoInline(admin.TabularInline):
  model=OrdenAsiento
  extra=0
  def get_readonly_fields(self, request, obj=None):
    if request.user.is_superuser or request.user.groups.filter(name="Cobranza").exists():
      return super(OrdenAsientoInline, self).get_readonly_fields(request, obj)
    else:
      return ('asiento','seccion','mesa','tipo','precio')

CONTENT_HELP_TEXT = ' '.join(['<p>*Importante: Recuerde cobrar y despues cambiar',
                              'el status a pagado antes de imprimir el boleto.',
                              '<br/>'])
class OrdenAdmin(ButtonAdmin):
  def queryset(self, request):
    qs = super(OrdenAdmin, self).queryset(request)
    if request.user.is_superuser or request.user.groups.filter(name="Cobranza").exists():
      return qs     
    else:
      return qs.filter(status_impresion="NO")
  def bar(self, request, obj=None):
    if obj != None: orderid=obj.pk
    url = reverse('ticket',kwargs={'id':orderid})
    return HttpResponseRedirect(url)
    #return HttpResponse(url) # Redirect or Response or None
  bar.short_description='Ticket'
  change_buttons = [ bar ]
  list_display = ('clave_reservacion', 'status', 'fecha_show','PrinTicket')
  search_fields = ('nombre', 'apellido','clave_reservacion','vendedor__nombre')
  list_filter = ('fecha_show','status')
  date_hierarchy = 'fecha_show'
  ordering = ('-clave_reservacion',)
  inlines=[OrdenAsientoInline]
  fieldsets = (
    ('Importantes en taquilla', {'fields': ('vendedor','forma_pago','folio_cupon','cambio_dolar','status','status_impresion'),'description': '<div class="help">%s</div>' % CONTENT_HELP_TEXT,}),
    (None, {'fields': ('clave_reservacion', 'show','fecha_show','horario_id',)}),
    ('Datos del cliente', {'fields': ('nombre', 'apellido', 'telefono','email')}),
    ('Totales de la compra', {'fields': ('total_dolares','monto_anticipo_dolares','total_pagar_dolares','total_pesos','monto_anticipo_pesos','total_pagar_pesos','fecha_pago','confirmacion_pago','tipo_tarjeta_pago','anotaciones','codigo_retorno')}),
    
  )
  def get_readonly_fields(self, request, obj=None):
    if request.user.is_superuser or request.user.groups.filter(name="Cobranza").exists():
      return super(OrdenAdmin, self).get_readonly_fields(request, obj)
    else:
      return ('clave_reservacion', 'show','fecha_show','nombre', 'apellido', 'telefono','email','total_dolares','monto_anticipo_dolares','total_pagar_dolares','total_pesos','monto_anticipo_pesos','total_pagar_pesos',OrdenAsientoInline)

class OrdenAsientoAdmin(admin.ModelAdmin):
  list_display = ('orden', 'asiento', 'mesa','tipo')
  search_fields = ('orden__clave_reservacion', 'asiento')
  ordering = ('-orden',)

class HorarioAsietoAdmin(admin.ModelAdmin):
  list_display =('horario','asiento','status','fecha')
  date_hierarchy = 'fecha'
  search_fields = ('horario__show__nombre','asiento__mesa','horario__fecha')
  list_filter = ('horario__show','horario__fecha','status')
  ordering=('-fecha',)


class HorarioAdmin(admin.ModelAdmin):
  list_display=('fecha','show')
  ordering =('fecha',)

class slideHomeAdmin(admin.ModelAdmin):
  list_display=('id','orden',)

admin.site.register(slideHome,slideHomeAdmin)
admin.site.register(Show)
admin.site.register(fotosGallery) 
admin.site.register(Horario,HorarioAdmin)
admin.site.register(Asiento,AsientoAdmin)
admin.site.register(HorarioAsiento,HorarioAsietoAdmin)
admin.site.register(Contacto)
admin.site.register(Orden, OrdenAdmin) 
admin.site.register(Artista)
admin.site.register(Vendedor,VendedorAdmin)
admin.site.register(OrdenAsiento,OrdenAsientoAdmin)
admin.site.register(video)
admin.site.register(FormaPago)
admin.site.register(TipoCambio)
admin.site.register(CustomText)

