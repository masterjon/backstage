# -*- encoding: utf-8 -*-
from django.shortcuts import render ,get_object_or_404
from django.conf import settings
from django.template import RequestContext
from main.models import *
from django.core.mail import send_mail
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core import serializers
from django.contrib.auth.views import login, logout
from datetime import datetime
from datetime import timedelta
import datetime as datetime2
from pytz import timezone
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from django.utils.http import urlencode,urlunquote
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import feedparser
import urllib2
import hashlib
import json
from django.core.urlresolvers import reverse


def home(request):
	shows = Show.objects.filter(ficha_visible=True)
	slides= slideHome.objects.order_by('orden')  
	return render(request,'home.html',{'shows':shows,'slides': slides})         


def groups(request):
	errors = []
	message = ''
	if request.is_ajax() and request.method=='POST':
		if not request.POST.get('nombre', ''):
			errors.append('<li>Enter a name.</li>')
		if not request.POST.get('email','') :
			errors.append('<li>Enter e-mail address.</li>')
		elif '@' not in request.POST['email']:
			errors.append('<li>Enter a valid e-mail address.</li>')
		if not errors:
			hiddenpost=["cmd","csrfmiddlewaretoken","x","y"]
			for key, value in request.POST.iteritems():
				if key not in hiddenpost:
					message=message+key+": "+value+"\n"
			send_mail("Contacto de Reserva de Grupos Backstage Cancún",message,request.POST.get('email'), ['mkt@backstagecancun.com']) 
			return HttpResponse("<span>Your data has been sent...</span>")
		return HttpResponse('<ul>'+''.join(errors)+'</ul>')
	return render(request, 'groups.html', {'errors': errors}) 


def contact(request):
	errors = []
	message = ''
	if request.is_ajax() and request.method=='POST':
		if not request.POST.get('nombre', ''):
			errors.append('<li>Enter a name.</li>')
		if not request.POST.get('email','') :
			errors.append('<li>Enter e-mail address.</li>')
		elif '@' not in request.POST['email']:
			errors.append('<li>Enter a valid e-mail address.</li>')
		if not errors:
			hiddenpost=["cmd","csrfmiddlewaretoken","x","y"]
			for key, value in request.POST.iteritems():
				if key not in hiddenpost:
					message=message+key+": "+value+"\n"
			send_mail("Contacto Backstage Cancún",message,request.POST.get('email'), ['mkt@backstagecancun.com']) 
			return HttpResponse("<span>Your data has been sent...</span>")
		return HttpResponse('<ul>'+''.join(errors)+'</ul>')
	return render(request, 'contact.html', {'errors': errors})


def tickets(request):
	if request.method=='POST':
		if request.POST.get('show') and request.POST.get('fecha'):
			try:
				tickets=Horario.objects.filter(fecha__month=request.POST['fecha'],show__id=request.POST['show']).order_by('fecha')
			except Exception, e:
				tickets=Horario.objects.order_by('fecha')
		elif request.POST.get('show') and not request.POST.get('fecha'):
			try:
				tickets=Horario.objects.filter(show__id=request.POST['show']).order_by('fecha')
			except Exception, e:
				tickets=Horario.objects.order_by('fecha')
		elif not request.POST.get('show') and  request.POST.get('fecha'): 
			try:
				tickets=Horario.objects.filter(fecha__month=request.POST['fecha']).order_by('fecha')
			except Exception, e:
				tickets=Horario.objects.order_by('fecha')
		else:
			tickets=Horario.objects.order_by('fecha')
	else:
		#muestra solo los horarios de la fecha actual en adelante
		hoy=datetime.now()+timedelta(hours=-12) #6 hrs de diferencia utc-cancun + 5 que dura el show  
		tickets=Horario.objects.exclude(fecha__lt=hoy).order_by('fecha')	
	#tickets=Horario.objects.order_by('fecha')
	shows=Show.objects.all()
	#tickets=Horario.objects.filter(fecha__month='06').order_by('fecha')
	#tickets=Horario.objects.filter(show__id='Deseo')
	return render(request,'tickets.html',{'tickets':tickets,'shows':shows})


def ticket(request,id):
	orden=Orden.objects.get(id=id)
	asientos= OrdenAsiento.objects.filter(orden=orden)
	#html=''

		#plaintext = get_template('ticket.txt')
	#htmly     = get_template('ticket.html')
	#d = Context({})
		#text_content = plaintext.render(d)
	#html_content = htmly.render(d)
	#return HttpResponse(html_content)	
	return render(request,'ticket.html',{'orden':orden,'asientos':asientos,'fecha': datetime.now()}) 


def deletecart(request):
	try:
		del request.session['cart']

	except KeyError:
		pass
	item2=CartItem()
	return HttpResponse("<h1>Carrito Borrado</h1>")	


def cart(request):
	if request.is_ajax() and request.method=='POST' and request.POST.get('cmd')=='delete':
		del request.session['cart'][int(request.POST.get('id_delete'))]
		html=''
		id=0
		total=0
		for item in request.session['cart']:
			total+=item.price
			html+='<tr>'
			html+='<td>'+item.seccion+'</td>'         
			html+='<td>'+str(item.mesa)+'</td>'   
			html+='<td>'+str(item.asiento)+'</td>'
			html+='<td>'+str(item.tipo)+'</td>'
			html+='<td>'+str(item.price)+' USD</td>' 
			html+='<td><i class="icon-remove-sign" onclick="del_cartitem(\''+str(id)+'\',\''+str(item.asiento)+'\',\''+str(item.mesa)+'\')"></i></td>'
			id+=1
		html+='<tr id="total">'
		html+='<td colspan="6" >Total:'+str(total)+' USD</td>'
		html+='</tr>'	
		payload = {'success': True, 'message': 'mes', 'data':html}

	if request.is_ajax() and request.method=='POST' and request.POST.get('cmd')=='add':
		asiento= request.POST['seat'] # Numero de asiento
		horario= request.POST['horario'] #id del horario
		seccion=request.POST['section']	#seccion del asiento
		tipo= request.POST['type'] #tipo de boleto, niño o adulto
		mesa= request.POST['table'] #mesa
		try:
			Objasiento= Asiento.objects.get(seccion=seccion,asiento=asiento,mesa=mesa) 
		except Asiento.DoesNotExist:
			return HttpResponse('Error Asiento')
		else:
			try:
				ObjHorario=Horario.objects.get(id=horario)
			except Horario.DoesNotExist:
				return HttpResponse('Error Horario')
			else:
				try:
					ObjHorarioAsiento = HorarioAsiento.objects.get(horario=ObjHorario,asiento=Objasiento)
				except HorarioAsiento.DoesNotExist:
					pass
				else:
					if ObjHorarioAsiento.status=='RE' or ObjHorarioAsiento.status=='DE' or ObjHorarioAsiento.status=='RP':
						#return HttpResponse('Asiento Ocupado')
						payload = {'success': False, 'message': 'Asiento Ocupado'}
						return HttpResponse(json.dumps(payload),content_type='application/json',)
		quantity=1
		if tipo =='adulto':
			if seccion =='1':
				price=ObjHorario.precio_s1_adulto
			elif seccion == '2':
				price=ObjHorario.precio_s2_adulto
			else:
				price=ObjHorario.precio_s3_adulto
		else:
			if seccion =='1':
				price=ObjHorario.precio_s1_nino
			elif seccion == '2':
				price=ObjHorario.precio_s2_nino
			else:
				price=ObjHorario.precio_s3_nino
		if 'cart' not in request.session:
			request.session['cart'] = [] #Crear el carrito de compras
		citem=CartItem()
		citem.asiento=asiento
		citem.quantity=quantity
		citem.price=price
		citem.idhorario=horario
		citem.mesa=mesa
		citem.seccion=seccion
		citem.idasiento=Objasiento.id
		citem.tipo=tipo
		citem.save()
		flag=False
		id=0
		for item in request.session['cart']:
			try:
				ObjA= Asiento.objects.get(seccion=item.seccion,asiento=item.asiento,mesa=item.mesa)
			except Asiento.DoesNotExist:
				pass
			else:
				try:
					ObjH=Horario.objects.get(id=item.idhorario)
				except Horario.DoesNotExist:
					pass
				else:
					try:
						ObjAH = HorarioAsiento.objects.get(horario=ObjH,asiento=ObjA)
					except HorarioAsiento.DoesNotExist:
						pass
					else:
						if ObjAH.status=='RE' or ObjAH.status=='DE' or ObjAH.status=='RP':
							del request.session['cart'][id]
			if item.idasiento==Objasiento.id:
				flag=True
			id+=1
		if not flag:
			request.session['cart'].append(citem)
		html=''
		id=0
		total=0
		for item in request.session['cart']:
			total+=item.price
			html+='<tr>'
			html+='<td>'+item.seccion+'</td>'
			html+='<td>'+str(item.mesa)+'</td>'   
			html+='<td>'+str(item.asiento)+'</td>'
			html+='<td>'+str(item.tipo)+'</td>'
			html+='<td class="item-price">'+str(item.price)+' USD</td>'
			html+='<td><i  onclick="del_cartitem(\''+str(id)+'\',\''+str(item.asiento)+'\',\''+str(item.mesa)+'\')" class="icon-remove-sign"></i></td>'
			html+='</tr>'
			id+=1
		html+='<tr id="total">'
		html+='<td colspan="6" >Total:'+str(total)+' USD</td>'
		html+='</tr>'	
		payload = {'success': True, 'message': 'mes', 'data':html}
	return HttpResponse(json.dumps(payload),content_type='application/json',)


def booking(request,id): 
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
		pass

	#if request.is_ajax() and request.method == 'POST':
	#	filtro='The beatles'
	#	filtro2=request.POST['show']
	#	horarios=ShowHorario.objects.filter(show=filtro2)
	#	return render(request,'show_horario.html',{'show_horarios':horarios})
	#else:
	#	show_list=ShowHorario.objects.all()
	
	show_horario=Horario.objects.get(id=id)
	lugares=HorarioAsiento.objects.filter(horario__id=id)
	asientos=[]
	selected=[]
	for lugar in lugares:
		asientos.append(lugar.asiento)
	data=serializers.serialize('json', asientos)
	try:
		del request.session['cart']

	except KeyError:
		pass
	# if 'cart' in request.session:
	# 	for item in request.session['cart']:
	# 		selected.append(item)

	data2=serializers.serialize('json', selected)
	return render(request,'booking.html',{'show_horario':show_horario,'lugares':lugares,'data':data,'data2':data2})


def checkout(request):
	if request.is_ajax() and request.method=='POST' and request.POST.get('cmd')=='view_seller':
		idvendedor= request.POST['vendedor']
		html=''
		try:
			vendedor=Vendedor.objects.get(id=idvendedor)
		except Vendedor.DoesNotExist:
			return HttpResponse('error')
		else:
			if vendedor.anticipo=='S':
				return HttpResponse('verdadero')
			else:
				return HttpResponse('error')
	asientos=0
	subtotal=0
	subtotal_pesos=0
	if request.method== 'POST':
		show_horario=Horario.objects.get(id=request.POST['horario'])
		vendedores= Vendedor.objects.all()
		if 'cart' in request.session:
			id=0
			for item in request.session['cart']: #Falta cambiarlo por horario 
				subtotal+=item.price
				seatobj=Asiento.objects.get(id=item.idasiento)
				try:
					HorarioAsiento.objects.get(horario=show_horario,asiento=seatobj)
				except:
					if request.user.is_authenticated():
						r=HorarioAsiento(horario=show_horario,asiento=seatobj,status='RE',fecha=datetime.now()) # Se confirma la reserva del carrito
					else:
						r=HorarioAsiento(horario=show_horario,asiento=seatobj,status='RP',fecha=datetime.now())
					r.save()					
				else:
					del request.session['cart'][id]
				id+=1
			cambio=12.5 #obtener ultimo tipo de cambio
			cambioObj=TipoCambio.objects.get(id=2)
			cambio=float(cambioObj.dolares)
			# try:
			# 	xml=urllib2.urlopen('http://www.dof.gob.mx/indicadores.xml')
			# except urllib2.URLError, e:
			# 	pass
			# else:
			# 	feed= feedparser.parse(xml)
			# 	if 'entries' in feed:
			# 		if feed['entries'][0]['title'] == 'DOLAR':
			# 			try:
			# 				cambio = float(feed['entries'][0]['summary_detail']['value'])
			# 			except:
			# 				pass
			subtotal_pesos=float(subtotal)*cambio
			request.session['cambio']=cambio
		
		if subtotal == 0 or subtotal_pesos== 0:
			return HttpResponseRedirect(reverse('booking',kwargs={'id':request.POST['horario']}))
	else:
		return HttpResponseRedirect('/tickets')
	return render(request,'checkout.html',{'show':show_horario,'subtotal':subtotal,'subtotal_pesos':subtotal_pesos,'vendedores': vendedores})

def confirm(request):
	errors=[]
	if request.method=='POST':
		#obtenemos los datos del cliente , vendedor y cantidad de anticipo
		if not request.POST.get('nombre', ''):
			errors.append('<li>Ingresa un nombre.</li>')
		if not request.POST.get('apellido', ''):
			errors.append('<li>Ingresa un apellido.</li>')
		if not request.POST.get('email','') :
			errors.append('<li>Ingresa un correo</li>')
		elif '@' not in request.POST['email']:
			errors.append('<li>Ingresa un e-mail a valido.</li>')
		#if not request.POST.get('telefono'):
			#errors.append('<li>Ingresa un telefono</li>')
		if not errors:
			if not request.POST.get('vendedor',''): #si no proporciona vendedor se asigna a Publico en General
				vendedor=Vendedor.objects.get(id=1018)
			else:
				vendedor=Vendedor.objects.get(id=request.POST['vendedor'])

			try:
				monto_anticipo_dolares= request.POST.get('anticipo','')
				monto_anticipo_pesos= request.POST.get('anticipo','')* request.session['cambio']
			except:
				monto_anticipo_dolares=0
				monto_anticipo_pesos=0
			else:
				pass
			forma_pago=FormaPago.objects.get(id=8)
			dt = datetime.now()
			fecha = DateFormat(dt)
			fecha.format(get_format('DATE_FORMAT'))
			fecha = fecha.format('Ymd')
			horario_show= request.POST['show']

			#se calcula el total a pagar en pesos y dolares. Se resta el valor del anticipo en caso de que exista.
			total_dolares=0
			if 'cart' in request.session:
				for item in request.session['cart']:
					total_dolares+=item.price
				total_pesos= float(total_dolares)*float(request.session['cambio'])
				total_pagar_pesos=0
				if monto_anticipo_dolares>0:
					modo_pago= 'RE'
					total_pagar_dolares= float(total_dolares) - float(monto_anticipo_dolares)
					total_pagar_pesos= float(total_pesos) - float(monto_anticipo_pesos) 
				else:
					modo_pago = 'RE' #dependiendo del moodo de pago se debe colocar pagado o reservado.
					total_pagar_dolares=float(total_dolares)
					total_pagar_pesos= float(total_pesos)

			#generamos la clave de reservación (modopago+fecha+show+order.id) y guardamos la orden
			try: 
				obj_horario=Horario.objects.get(id=horario_show)
				obj_show= obj_horario.show
				order=Orden(nombre=request.POST['nombre'],apellido=request.POST['apellido'],email=request.POST['email'],telefono=request.POST['telefono'],forma_pago=forma_pago,vendedor=vendedor,fecha=datetime.now(),status='RE',monto_anticipo_dolares=monto_anticipo_dolares,total_dolares=total_dolares,total_pagar_dolares=total_pagar_dolares,monto_anticipo_pesos=monto_anticipo_pesos,total_pesos=total_pesos,total_pagar_pesos=total_pagar_pesos,show=obj_show,fecha_show=obj_horario.fecha)
				order.save()
				#clave_res= str(modo_pago) + '-' + str(fecha) + '-' + str(show)+'-'+str(order.id)
				clave_res= str(modo_pago)+str(fecha)+str(horario_show)+str(order.id)
				order.clave_reservacion=clave_res
				order.save()

				#para cada elemento del carrito(en sesion) se asocia a la orden correspondiente y se almacena en la BD 
				if 'cart' in request.session:
					for item in request.session['cart']:
						order_item=OrdenAsiento(orden=order,asiento=item.asiento,seccion=item.seccion,mesa=item.mesa,tipo=item.tipo,precio=item.price)
						order_item.save() 
			except:
				return render(request,'error.html')
			#si se guardo exitosamente la orden, se envia correo al usuario
			else:
				try:
					show_horario=Horario.objects.get(id=horario_show)
				except Horario.DoesNotExist:
					pass
				else:
					html=''
					plaintext = get_template('email.txt')
					htmly     = get_template('email.html')
					cart= request.session['cart']
					#total_pesos= float(total_pagar_dolares)*request.session['cambio']
					nombre_comprador=request.POST['nombre']+" "+request.POST['apellido']
					d = Context({ 'clave_reservacion': clave_res,'show': show_horario.show.nombre,'fecha': show_horario.fecha,'total': total_pagar_dolares,'boletos':cart,'total_pesos':total_pagar_pesos,'nombre_comprador':nombre_comprador} )
					subject, from_email, to ,bcc = 'Reservación BackStage - '+clave_res, 'reservaciones@backstagecancun.com', request.POST['email'],"reservaciones@backstagecancun.com"
					text_content = plaintext.render(d)
					html_content = htmly.render(d)
					msg = EmailMultiAlternatives(subject, text_content, from_email, [to],[bcc])
					msg.attach_alternative(html_content, "text/html")
					msg.send()
					try:
						del request.session['cart']
					except KeyError:
						pass
					return render(request,'success.html',{'mailing':html_content})
	return HttpResponseRedirect('/tickets')


def payment(request):
	errors=[]
	if request.method=='POST':
		#obtenemos los datos del cliente , vendedor y cantidad de anticipo
		if not request.POST.get('nombre', ''):
			errors.append('<li>Ingresa un nombre.</li>')
		if not request.POST.get('apellido', ''):
			errors.append('<li>Ingresa un apellido.</li>')
		if not request.POST.get('email','') :
			errors.append('<li>Ingresa un correo</li>')
		elif '@' not in request.POST['email']:
			errors.append('<li>Ingresa un e-mail a valido.</li>')
		#if not request.POST.get('telefono'):
			#errors.append('<li>Ingresa un telefono</li>')
		if not errors:
			if not request.POST.get('vendedor',''): #si no proporciona vendedor se asigna a Publico en General
				vendedor=Vendedor.objects.get(id=1018)
			else:
				vendedor=Vendedor.objects.get(id=request.POST['vendedor'])

			try:
				monto_anticipo_dolares= request.POST.get('anticipo','')
				monto_anticipo_pesos= request.POST.get('anticipo','')* request.session['cambio']
			except:
				monto_anticipo_dolares=0
				monto_anticipo_pesos=0
			else:
				pass
			forma_pago=FormaPago.objects.get(id=20)  #id:20=TARJETA DE CREDITO/DEBITO - INTERNET
			dt = datetime.now()
			fecha = DateFormat(dt)
			fecha.format(get_format('DATE_FORMAT'))
			fecha = fecha.format('Ymd')
			horario_show= request.POST.get('show')

			#se calcula el total a pagar en pesos y dolares. Se resta el valor del anticipo en caso de que exista.
			total_dolares=0
			if 'cart' in request.session:
				for item in request.session['cart']:
					total_dolares+=item.price
				total_pesos= float(total_dolares)*float(request.session['cambio'])
				total_pagar_pesos=0
				if monto_anticipo_dolares>0:
					modo_pago= 'RE'
					total_pagar_dolares= float(total_dolares) - float(monto_anticipo_dolares)
					total_pagar_pesos= float(total_pesos) - float(monto_anticipo_pesos) 
				else:
					modo_pago = 'RE' #dependiendo del moodo de pago se debe colocar pagado o reservado.
					total_pagar_dolares=float(total_dolares)
					total_pagar_pesos= float(total_pesos)

			#generamos la clave de reservación (modopago+fecha+show+order.id) y guardamos la orden
			try: 
				obj_horario=Horario.objects.get(id=horario_show)
				obj_show= obj_horario.show
				order=Orden(nombre=request.POST['nombre'],apellido=request.POST['apellido'],email=request.POST['email'],telefono=request.POST['telefono'],forma_pago=forma_pago,vendedor=vendedor,fecha=datetime.now(),status='PE',monto_anticipo_dolares=monto_anticipo_dolares,total_dolares=total_dolares,total_pagar_dolares=total_pagar_dolares,monto_anticipo_pesos=monto_anticipo_pesos,total_pesos=total_pesos,total_pagar_pesos=total_pagar_pesos,show=obj_show,fecha_show=obj_horario.fecha,horario_id=obj_horario.id)
				order.save()
				#clave_res= str(modo_pago) + '-' + str(fecha) + '-' + str(show)+'-'+str(order.id)
				clave_res= str(modo_pago)+str(fecha)+str(horario_show)+str(order.id)
				order.clave_reservacion=clave_res
				order.save()

				#para cada elemento del carrito(en sesion) se asocia a la orden correspondiente y se almacena en la BD 
				if 'cart' in request.session:
					for item in request.session['cart']:
						order_item=OrdenAsiento(orden=order,asiento=item.asiento,seccion=item.seccion,mesa=item.mesa,tipo=item.tipo,precio=item.price)
						order_item.save() 
			except:
				return render(request,'error.html')
			#si se guardo exitosamente la orden, se envian los datos a la pasarela de pago de First Data 
			else:
				parameters={}
				url="https://www.thepayplace.com/backstage/cancun/epayments/default.aspx?"
				returnurl="http://backstagecancun.com/postpayment/"
				parameters['returnurl']=returnurl  #url a donde de nuestra pagina donde se dirigira  despues de la pasarela de pago
				parameters['id']=order.id #numero de id de la orden
				parameters['ref']=order.clave_reservacion #numero referencia de la orden 
				parameters['amount']=str(total_pesos)  #cantidad a pagar 
				parameters['bfn']=request.POST['nombre'] 
				parameters['bln']=request.POST['apellido']
				parameters['bem']=request.POST['email']
				parameters['bph']=request.POST.get('telefono', '')
				#el campo custom nos sirve para que el usuario pueda visualizar cierta informacion en la pasarela de pago
				#los campos van separados por comas y se administran desde el panel de First Data
				#en este caso solo ocupamos 2: el nombre del show concatenado con la fecha y el monto a pagar
				parameters['custom']=obj_show.nombre+"("+str(obj_horario.fecha.strftime('%d-%m-%Y'))+"),"+parameters['amount']
				#hacemos un encode de los datos y le conccatenamos la url de paypoint
				redirectUrl=url+urlencode(parameters)   
			#return HttpResponse(redirectUrl)
			return HttpResponseRedirect(redirectUrl)
	return HttpResponseRedirect(reverse('tickets'))


def postpayment(request):
	
	return_code=request.GET.get('c',0)
	message=urlunquote(request.GET.get('m',''))
	orderid=request.GET.get('i',0)
	total_amount_charged=request.GET.get('t','')
	confitmation_number=request.GET.get('o','')
	remote_hash=request.GET.get('hash','')
	payment_submission_date=urlunquote(request.GET.get('d',''))
	payment_card=urlunquote(request.GET.get('ct',''))
	try: 
		order=Orden.objects.get(id=orderid)
	except Orden.DoesNotExist:
		local_hash=hashlib.sha1("")
		order_total=0
	else:
		order_total=order.total_pagar_pesos
		local_hash=hashlib.sha1(confitmation_number+str(order_total)+settings.SECURITY_KEY)
		#verificamos que no se haya procesado la orden anteriormente 
		if order.codigo_retorno is None:
			
			order.anotaciones=message
			order.codigo_retorno=return_code
			order.save()
		else:
			return HttpResponse("Esta orden ya a sido procesada")
		#Retun Code:
		#2 Payment succes
		#4 Error
		#5 Declined
		#7 Communicarion Error
	    #13 Unaccepted Card Type
    
	if return_code == "2":
		#comprobamos que con el hash que el monto de pago no haya sido modificadoyy
		if remote_hash==local_hash.hexdigest().lower or remote_hash==local_hash.hexdigest().upper():
			#enviar correo
			order.status="PG"
			order.fecha_pago=datetime.strptime(payment_submission_date, "%m/%d/%Y")
			order.tipo_tarjeta_pago=payment_card
			order.confirmacion_pago=confitmation_number
			order.save()
			
			#se envia el correo informando al cliente de su reservacion
			seats=order.ordenasiento_set.all()
			html_content=order.SendMail(seats)
			request.session['mailing']=html_content
			
			#marcar como reservado el horarioasiento
			horario=Horario.objects.get(id=order.horario_id)
			for seat in seats:
				asiento=Asiento.objects.get(seccion=seat.seccion,asiento=seat.asiento,mesa=seat.mesa)
				Horario_asiento=HorarioAsiento.objects.get(asiento=asiento,horario=horario)
				Horario_asiento.status='RE'
				Horario_asiento.save()
			
			#guardar fecha de pago 
			#guardar autorization code
			#guardar confirmation nuber

			#cambiar forma de pago a Online(en la view de payment)
			try:
				del request.session['cart']
			except KeyError:
				pass
			#return render(request,'success.html',{'mailing':html_content})
			return HttpResponseRedirect(reverse('success'))

		else:
			order.anotaciones="El pago fue exitoso pero la cantidad pagada no corresponde"
			return HttpResponse("Error: incomplete payment")
	else:
		# html="<h1>Tu pago no pudo ser procesado. Por favor intente de nuevo</h1>"
		# html+="<h2>Mensaje:"+message+"</h2>"
		# return HttpResponse(html)
		return HttpResponseRedirect(reverse('tickets'))



def success(request):
	if 'mailing' in request.session:
		html_content=request.session['mailing']
		del request.session['mailing']
	return render(request,'success.html',{'mailing':html_content})

def error(request):
	return render(request,'error.html')

def timeout(request,id):
	if 'cart' in request.session:
		for item in request.session['cart']:
			try:
				ObjA= Asiento.objects.get(seccion=item.seccion,asiento=item.asiento,mesa=item.mesa)
			except Asiento.DoesNotExist:
				pass
			else:
				try:
					ObjH=Horario.objects.get(id=item.idhorario)
				except Horario.DoesNotExist:
					pass
				else:
					try:
						ObjAH = HorarioAsiento.objects.get(horario=ObjH,asiento=ObjA,status='RP')
					except HorarioAsiento.DoesNotExist:
						pass
					else:
						if ObjAH.status=='RP':
							ObjAH.delete()       
	try:
		del request.session['cart']
	except KeyError:
		pass
	horario=id #Id del horario a ser redireccionado
	return render(request,'timeout.html',{'horario':horario})


def gallery(request):
	videos= video.objects.all()
	galeria= fotosGallery.objects.all()
	return render(request,'fotosgallery.html',{'videos': videos, 'galeria': galeria}) 


def galleryinterior(request,id):
	fotos=fotosGallery.objects.filter(numero_categoria=id)
	return render(request,'galleryInt.html',{'fotos': fotos}) 


def obj_list(request,model):
	obj_list = model.objects.all()
	template_name = '%s.html' % model.__name__.lower()
	var_name = '%s_list' % model.__name__.lower()
	return render(request,template_name,{var_name: obj_list}) 
	

def static_page(request,template):
	template_name=template 
	return render(request,template_name)
	
def show(request,slug):
	show = get_object_or_404(Show,slug=slug)
	artistas= Artista.objects.filter(show__id=show.id)
	return render(request,'show.html',{'show':show,'artistas':artistas})


def report(request):
	if request.method == 'POST':
		arguments = {}
		if request.POST.get('show__id', ''):
			try:
				show = Show.objects.get(id = request.POST.get('show__id'))
				show_nombre = show.nombre
			except:
				show_nombre = "Error"
		else:
			show_nombre = "Todos"

		if request.POST.get('forma_pago__id', ''):
			try:
				forma_pago = FormaPago.objects.get(id = request.POST.get('forma_pago__id'))
				forma_pago_nombre = forma_pago.forma_pago
			except:
				forma_pago_nombre = "Error"
		else:
			forma_pago_nombre = "Todas"

		if request.POST.get('status', ''):
			status = request.POST.get('status')
		else:
			status="Todos"
		if request.POST.get('vendedor__id', ''):
			try:
				vendedor = Vendedor.objects.get(id = request.POST.get('vendedor__id'))
				vendedor_nombre = vendedor.nombre 
			except:
				vendedor_nombre = "Error"
		else:
			vendedor_nombre = "Todos"

		titulo = "Show:" + show_nombre + " | Forma Pago:" + forma_pago_nombre + " | Status:"+status+" | Vendedor:"+vendedor_nombre+" | Fecha:"+request.POST.get('fechainicio', '')+"-"+request.POST.get('fechafin', '')
		for k, v in request.POST.items():
			if v and k in ["show__id","forma_pago__id","status","vendedor__id"]:
				arguments[k] = v
		if not request.POST.get('fechainicio','') or not request.POST.get('fechafin',''):
			return HttpResponse("El campo fecha es obligatorio <a href="+reverse('report')+">Regresar</a>")
		fechainicio=datetime.strptime(request.POST['fechainicio'],'%m/%d/%Y').date()
		fechafin=datetime.strptime(request.POST['fechafin'],'%m/%d/%Y').date()
		one_day=timedelta(days=1)
		fechafin=fechafin+one_day #Filtering a DateTimeField with dates wont include items on the last day, because the bounds are interpreted as 0am on the given date
		orders = Orden.objects.filter(**arguments).filter(fecha_show__range=(fechainicio,fechafin)).order_by('clave_reservacion')
		s1_adulto=0
		s2_adulto=0
		s3_adulto=0
		s1_nino=0
		s2_nino=0
		s3_nino=0
		totales=[]
		for order in orders:
			for asiento in order.ordenasiento_set.all():
				if asiento.seccion=="1" and asiento.tipo=="adulto":s1_adulto+=1
				if asiento.seccion=="2" and asiento.tipo=="adulto":s2_adulto+=1
				if asiento.seccion=="3" and asiento.tipo=="adulto":s3_adulto+=1
				if asiento.seccion=="1" and asiento.tipo=="nino":s1_nino+=1
				if asiento.seccion=="2" and asiento.tipo=="nino":s2_nino+=1
				if asiento.seccion=="3" and asiento.tipo=="nino":s3_nino+=1
		totales=dict(s1_adulto=s1_adulto,s2_adulto=s2_adulto,s3_adulto=s3_adulto,s1_nino=s1_nino,s2_nino=s2_nino,s3_nino=s3_nino)
					
	else: 
		orders=None 
		totales=None
		titulo=""
	forma_pago=FormaPago.objects.order_by('forma_pago')
	shows=Show.objects.order_by('nombre')
	vendedores=Vendedor.objects.order_by('nombre')
	return render(request,'report.html',{'orders':orders,'forma_pago':forma_pago,'shows':shows,'vendedores':vendedores,'totales':totales,'titulo':titulo})


def report2(request):
	if request.method == 'POST':
		arguments = {}
		if request.POST.get('show__id', ''):
			try:
				show = Show.objects.get(id = request.POST.get('show__id'))
				show_nombre = show.nombre
			except:
				show_nombre = "Error"
		else:
			show_nombre = "Todos"
		if request.POST.get('status', ''):
			status = request.POST.get('status')
		else:
			status="Todos"
		titulo = "Show:" + show_nombre + " |  Fecha:"+request.POST.get('fechainicio', '')+"-"+request.POST.get('fechafin', '')
		for k, v in request.POST.items():
			if v and k in ["show__id","status"]:
				arguments[k] = v
		if not request.POST.get('fechainicio','') or not request.POST.get('fechafin',''):
			return HttpResponse("El campo fecha es obligatorio <a href="+reverse('report')+">Regresar</a>")
		fechainicio=datetime.strptime(request.POST['fechainicio'],'%m/%d/%Y').date()
		fechafin=datetime.strptime(request.POST['fechafin'],'%m/%d/%Y').date()
		one_day=timedelta(days=1)
		fechafin=fechafin+one_day #Filtering a DateTimeField with dates wont include items on the last day, because the bounds are interpreted as 0am on the given date
		ordenes = Orden.objects.filter(**arguments).filter(fecha_show__range=(fechainicio,fechafin)).order_by('clave_reservacion')
		vendedores=Vendedor.objects.order_by('id').values('id')
		vendedores_ordenes={}
		s1_adulto=0
		s2_adulto=0
		s3_adulto=0
		s1_nino=0
		s2_nino=0
		s3_nino=0
		total_dolares=0
		monto_anticipo_dolares=0
		total_pagar_dolares=0
		total_pesos=0
		monto_anticipo_pesos=0
		total_pagar_pesos=0
		totales=[]
		# Se crea en el diccionario una lista por cada vendedor
		# y dentro de cada lista iran las ordenes asociadas al vendedor
		# Por ultimo se sacan los totales de los asientos
		for vendedor in vendedores:
			this_id=str(vendedor['id'])
			vendedores_ordenes.update({this_id:[]})
			for orden in ordenes:
				if orden.vendedor_id==vendedor['id']:
					vendedores_ordenes[this_id].append(orden)

					total_dolares+=orden.total_dolares
					monto_anticipo_dolares+=orden.monto_anticipo_dolares
					total_pagar_dolares+=orden.total_pagar_dolares
					total_pesos+=orden.total_pesos
					monto_anticipo_pesos+=orden.monto_anticipo_pesos
					total_pagar_pesos+=orden.total_pagar_pesos

					for asiento in orden.ordenasiento_set.all():
						if asiento.seccion=="1" and asiento.tipo=="adulto":s1_adulto+=1
						if asiento.seccion=="2" and asiento.tipo=="adulto":s2_adulto+=1
						if asiento.seccion=="3" and asiento.tipo=="adulto":s3_adulto+=1
						if asiento.seccion=="1" and asiento.tipo=="nino":s1_nino+=1
						if asiento.seccion=="2" and asiento.tipo=="nino":s2_nino+=1
						if asiento.seccion=="3" and asiento.tipo=="nino":s3_nino+=1
			if len(vendedores_ordenes[this_id])==0:    #Se elimina el elemento del dicionario si no hubo ordenes asociadas al vendedor
				del vendedores_ordenes[this_id]
		totales=dict(s1_adulto=s1_adulto,s2_adulto=s2_adulto,s3_adulto=s3_adulto,
			s1_nino=s1_nino,s2_nino=s2_nino,s3_nino=s3_nino,total_dolares=total_dolares,
			monto_anticipo_dolares=monto_anticipo_dolares,total_pagar_dolares=total_pagar_dolares,
			total_pesos=total_pesos,monto_anticipo_pesos=monto_anticipo_pesos,
			total_pagar_pesos=total_pagar_pesos)
	else:
		#vendedores=Vendedor.objects.exclude(orden__total_dolares=0)

		# Obtenemos las ordenes segun los filtros dados , el id de los vendedores y un diccionario
		# para almacenar 
		ordenes=None 
		totales=None
		titulo=""
		vendedores_ordenes={}
	vendedores=Vendedor.objects.order_by('id')		
	shows=Show.objects.order_by('nombre')

		#q=Vendedor.objects.filter(id=968).annotate(asientos=Count('orden__ordenasiento')).filter(asientos__seccion='1')
		#q=Vendedor.objects.extra(select={'asientos': 'SELECT COUNT(*) FROM main_ordenasiento WHERE main_orden.vendedor_id = main_vendedor.id AND main_orden.id=main_ordenasiento.orden_id AND seccion = 2'})

	return render(request,'report2.html',{'vendedores':vendedores,'shows':shows,'ordenes':ordenes,'vendedores_ordenes':vendedores_ordenes,'totales':totales,'titulo':titulo})


def report_excel(request):
	response=HttpResponse(request.POST['table'],mimetype='application/ms-excel; charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="reporte.xls"'
	return response

def mailing(request):
	errors = []
	message = 'Nuevo '
	if request.method == 'POST':
		if not request.POST.get('nombre1', ''):
			errors.append('<li>Nombre persona 1.</li>')
		if not request.POST.get('nombre2','') :
			errors.append('<li>Nombre persona 1.</li>')
		if not errors:
			hiddenpost=["enviar","csrfmiddlewaretoken","x","y"]
			for key, value in request.POST.iteritems():
				if key not in hiddenpost:
					message=message+key+": "+value+"\n"
			send_mail(
				"Contacto gran inauguracion backstagecancun",
				message,'graninauguracion@backstagecancun.com',['graninauguracion@backstagecancun.com'],
				#message,'jon@punkmkt.com',['jon@punkmkt.com'],
				)
			return HttpResponse("<span>Felicidades! Tu asistencia ha sido confirmada</span>")
		return HttpResponse('<ul>'+''.join(errors)+'</ul>')
	return render(request, 'mailing.html', {'errors': errors}) 

def update_print_status(request):
	if request.is_ajax() and request.method == 'POST':
		#orderid=request.POST['id_order']
		#Orden.objects.filter(id=orderid).update(status_impresion='SI')
		return HttpResponse("Success")
	else:
		return ("Try again")
