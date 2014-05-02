# -*- encoding: utf-8 -*-
from django.db import models
from sorl.thumbnail import ImageField
import locale
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from tinymce.models import HTMLField

from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
#locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")

# Create your models here.
class MenuComida(models.Model):
	nombre = models.CharField(max_length=50)
	entrada = models.TextField(blank=True)
	plato_fuerte = models.TextField(blank=True)
	postre = models.TextField(blank=True)
	imagen = models.ImageField(upload_to='menu_comida', verbose_name='Preview',null=True,blank=True)
	def __unicode__(self):
		return self.nombre


class slideHome(models.Model):
	imagen = ImageField(upload_to='slide_home', verbose_name='Slide',null=True,blank=True)
	orden= models.IntegerField()
	def __unicode__(self):
		return u"img-%s"% (self.id)

class Categoria(models.Model):
	idcategoria= models.IntegerField()
	nombre=models.CharField(max_length=50)
	def __unicode__(self):
		return self.nombre

class fotosGallery(models.Model):
	thumbnail = ImageField(upload_to='galeria/thumbnail',null=True,blank=True)
	imagen = ImageField(upload_to='galeria',null=True,blank=True)
	nombre=models.CharField(max_length=50)
	nombreen=models.CharField(max_length=50)
	categoria=models.CharField(max_length=50)
	categoriaen=models.CharField(max_length=50)
	numero_categoria= models.IntegerField(default=1)
	padre= models.BooleanField()
	def __unicode__(self):
		return u"img-%s Cat-%s"% (self.id,self.categoria)	
class video(models.Model):
	Preview = ImageField(upload_to='videos/thumbnail',null=True,blank=True)
	videoURL = models.URLField(max_length=300,blank=True)
	titulo = models.CharField(max_length=50)
	tituloen = models.CharField(max_length=50)
	def __unicode__(self):
		return u"video-%s"% (self.id)	

class Show(models.Model):
	nombre = models.CharField(max_length=50)
	slug = models.CharField(max_length=50, null=True)
	previewImg =  ImageField(upload_to='shows', verbose_name='Preview',null=True,blank=True)
	descripcion = models.TextField(blank=True)
	descripcionen = models.TextField(blank=True)
	img1 = ImageField(upload_to='shows/interiores', verbose_name='Imagen Interior',null=True,blank=True)
	img1_mobile = ImageField(upload_to='shows/interiores', verbose_name='Imagen Interior Movil',null=True,blank=True)
	videoURL = models.URLField(max_length=300,blank=True)
	sort = models.IntegerField(max_length=5, null=True,default=1)
	ficha_visible = models.BooleanField("El show se mostrara en el home de la web",default=True)
	descripcion_precios =models.TextField(blank=True)
	descripcion_preciosen =models.TextField(blank=True)
	def __unicode__(self):
		return self.nombre
def format_artista(instance, filename):
	return 'shows/'+instance.show.slug+'/'+filename
class Artista(models.Model):
	show = models.ForeignKey(Show, verbose_name='Show')
	nombre= models.CharField(max_length=50)
	nombreen= models.CharField(max_length=50)
	previewImg =  ImageField(upload_to=format_artista, verbose_name='Foto principal',null=True,blank=True)
	biografia= models.TextField(blank=True)
	biografiaen= models.TextField(blank=True)
	videoRulMp4 = models.URLField(max_length=300,blank=True)
	videoRulOgv = models.URLField(max_length=300,blank=True)
	def __unicode__(self):
		return self.nombre
		
class Asiento(models.Model):
	seccion = models.CharField(max_length=10)
	asiento = models.CharField(max_length=10)
	mesa = models.CharField(max_length=10)
	def __unicode__(self):
		return u"S:%s M:%s A:%s" % (self.seccion,self.mesa,self.asiento)

class Horario(models.Model):
	fecha= models.DateTimeField(unique=True)
	show = models.ForeignKey(Show, verbose_name='Show')
	precio_s1_adulto = models.DecimalField('Precio Adulto Seccion 1', default=119, null=True, max_digits=18,  decimal_places=2)
	precio_s2_adulto = models.DecimalField('Precio Adulto Seccion 2', default=99,null=True, max_digits=18,  decimal_places=2)
	precio_s3_adulto =	models.DecimalField('Precio Adulto Seccion 3',default=99,null=True,  max_digits=18,  decimal_places=2)
	precio_s1_nino = models.DecimalField('Precio Niño Seccion 1',default=89,null=True,  max_digits=18,  decimal_places=2)
	precio_s2_nino = models.DecimalField('Precio Niño Seccion 2',default=59,null=True,  max_digits=18,  decimal_places=2)
	precio_s3_nino = models.DecimalField('Precio Niño Seccion 3',default=59,null=True,  max_digits=18,  decimal_places=2)
	servicios_s1 = models.TextField('Servicios Seccion 1',blank=True,null=True)
	servicios_s2 = models.TextField('Servicios Seccion 2',blank=True,null=True)
	servicios_s3 = models.TextField('Servicios Seccion 3',blank=True,null=True)
	def __unicode__(self):
		return u"%s-%s" % (self.show,self.fecha.strftime('%a, %B %d, %Y-%I:%M %p'))
		
class HorarioAsiento(models.Model):
	DISPONIBLE = 'DI'
	RESERVADO = 'RE'
	DESHABILITADO = 'DE'
	RESERVADO_PENDIENTE = 'RP'
	STATUS_ASIENTO = (
        (DISPONIBLE, 'Disponible'),
        (RESERVADO, 'Reservado'), 
        (DESHABILITADO, 'Deshabilitado'),
        (RESERVADO_PENDIENTE, 'Reservado sin confirmación de pago')
    )
	horario = models.ForeignKey(Horario, verbose_name='Horario')
	asiento = models.ForeignKey(Asiento, verbose_name='Asiento')
	status = models.CharField(max_length=2,choices=STATUS_ASIENTO,default=DISPONIBLE)
	fecha = models.DateTimeField("Fecha de la reserva",blank=True,null=True)
	def __unicode__(self):
		return u"%s----%s" % (self.asiento,self.horario)
class Vendedor(models.Model):
	nombre=models.CharField(max_length=100,verbose_name='Nombre del hotel o agencia')
	canal=models.CharField(max_length=100,verbose_name='Canal de Venta')
	comision = models.DecimalField(default=0, max_digits=18,  decimal_places=2)
	SI='S'
	NO='N'
	OPCIONES=(
		(SI,'Si'),
		(NO,'NO'),
	)
	anticipo = models.CharField(max_length=2,choices=OPCIONES,default=NO)
	def __unicode__(self):
		return self.nombre
class FormaPago(models.Model):
	forma_pago= models.CharField(max_length=100,verbose_name='Forma de pago')
	def __unicode__(self):
		return self.forma_pago
class Orden(models.Model):
	forma_pago = models.ForeignKey(FormaPago, verbose_name='Forma de pago') 
	clave_reservacion = models.CharField(max_length=50)
	vendedor = models.ForeignKey(Vendedor, verbose_name='Vendedor')
	horario_id= models.IntegerField(null=True)
	show = models.ForeignKey(Show, verbose_name='Show') 
	fecha_show= models.DateTimeField("Horario del show")
	fecha = models.DateField("Fecha de la reserva")
	fecha_pago= models.DateField("Fecha de pago",blank=True,null=True)
	NO_IMPRESO='NO'
	IMPRESO='SI'

	STATUS_IMPRESION=(
		(NO_IMPRESO, 'No impreso'),
		(IMPRESO, 'Impreso'),
		)
	status_impresion = models.CharField(max_length=2,choices=STATUS_IMPRESION,default=NO_IMPRESO, blank=True)
	folio_cupon = models.CharField(max_length=50, blank=True)
	nombre =  models.CharField(max_length=50, blank=True)
	apellido =  models.CharField(max_length=50, blank=True)
	telefono =  models.CharField(max_length=50, blank=True)
	email=  models.CharField(max_length=100, blank=True)
	RESERVADO= 'RE'
	PAGADO= 'PG'
	PENDIENTE= 'PE'
	ANTICIPO= 'RA'
	CORTESIA= 'CO'
	STATUS_COMPRA=(
		(RESERVADO, 'Reservado'),
		(PAGADO, 'Pagado'),
		(PENDIENTE, 'Pendiente'), 
		(ANTICIPO, 'Anticipo'),
		(CORTESIA, 'Cortesía'),
		)
	status = models.CharField(max_length=2,choices=STATUS_COMPRA,default=PENDIENTE,verbose_name='Status de la reserva')
	total_dolares= models.DecimalField(default=0, max_digits=18,  decimal_places=2)
	monto_anticipo_dolares= models.DecimalField(default=0, null=True, max_digits=18,  decimal_places=2)
	total_pagar_dolares = models.DecimalField(default=0, null=True, max_digits=18,  decimal_places=2)
	total_pesos= models.DecimalField(default=0, max_digits=18,  decimal_places=2)
	monto_anticipo_pesos= models.DecimalField(default=0, null=True, max_digits=18,  decimal_places=2)
	total_pagar_pesos = models.DecimalField(default=0, null=True, max_digits=18,  decimal_places=2)
	cambio_dolar=models.DecimalField(default=12.5,null=True,max_digits=18,decimal_places=2)
	confirmacion_pago=models.CharField(max_length=50,blank=True,null=True)
	tipo_tarjeta_pago=models.CharField(max_length=10,blank=True,null=True)
	codigo_retorno=models.IntegerField(blank=True,null=True)
	anotaciones=models.TextField("Anotaciones extras",blank=True,null=True)

	def __unicode__(self):
		return self.clave_reservacion

	def PrinTicket(self):
		url = reverse('ticket',kwargs={'id':self.id})
		return mark_safe(u'<a target="_blank" href="%s">%s</a>' % (url, ugettext('View')))
	PrinTicket.allow_tags = True

	def SendMail(self,cart):
		html=''
		plaintext = get_template('email.txt')
		htmly     = get_template('email.html')
		#total_pesos= float(total_pagar_dolares)*request.session['cambio']

		nombre_comprador=self.nombre+" "+self.apellido
		d = Context({ 'clave_reservacion': self.clave_reservacion,'show': self.show,'fecha': self.fecha_show,'total': self.total_pagar_dolares,'boletos':cart,'total_pesos':self.total_pagar_pesos,'nombre_comprador':nombre_comprador} )
		subject, from_email, to ,bcc = 'Reservacion BackStage - '+self.clave_reservacion, 'reservaciones@backstagecancun.com', self.email,"reservaciones@backstagecancun.com"
		text_content = plaintext.render(d)
		html_content = htmly.render(d)
		msg = EmailMultiAlternatives(subject, text_content, from_email, [to],[bcc])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		return html_content


class OrdenAsiento(models.Model):
	orden = models.ForeignKey(Orden, verbose_name='Orden')
	asiento = models.CharField(max_length=10, blank=True)
	seccion = models.CharField(max_length=10, blank=True)
	mesa = models.CharField(max_length=10, blank=True)
	tipo = models.CharField(max_length=10, blank=True)
	precio = models.DecimalField(default=0, max_digits=18,  decimal_places=2)
	def __unicode__(self):
		return self.orden.clave_reservacion 
class Contacto(models.Model):
	nombre = models.CharField(max_length=50 ,blank=True)
	apellido = models.CharField(max_length=50, blank=True)
	correo = models.EmailField(max_length=75)
	telefono = models.CharField(max_length=50, blank=True)
	fecha_nacimiento = models.DateField(blank=True)
	fecha_creacion = models.DateField("Fecha de Creacion")
	
	def __unicode__(self):
		return self.correo
class CartItem(models.Model):
	asiento = models.CharField(max_length=10)
	quantity = models.IntegerField(default=1)
	price = models.DecimalField(default=20,null=True,  max_digits=18,  decimal_places=2)
	idhorario = models.IntegerField(default=1)
	mesa = models.CharField(max_length=10)
	seccion = models.CharField(max_length=10)
	idasiento = models.IntegerField(default=1)
	tipo=models.CharField(max_length=50)
	#def __init__(self, item, quantity):
    #    self.asiento = asiento
    #    self.quantity = quantity
    #    self.price = price
class TipoCambio(models.Model):
	dolares= models.DecimalField(default=12.5,null=True,  max_digits=10,  decimal_places=2)
	def __unicode__(self):
		return "Dolar"

class CustomText(models.Model):
	texto=models.TextField()


