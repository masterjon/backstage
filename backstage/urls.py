from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from main import models
from django.contrib.auth.views import login, logout
from django.core.urlresolvers import reverse_lazy

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'backstage.views.home', name='home'),
    # url(r'^backstage/', include('backstage.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^backadmin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',
            {'document_root':settings.MEDIA_ROOT, 'show_indexes': True}
    ),
    url(r'^fanpage/fb_backstage/(?P<path>.*)$', 'django.views.static.serve'),
    url(r'^$','main.views.home',name='home'),
    url(r'^groups/$', 'main.views.groups',name="groups"),
    url(r'^contact/$', 'main.views.contact',name="contact"),
    url(r'^pressroom/$', 'main.views.static_page', {'template': 'pressroom.html'},name="pressroom"),
    url(r'^tour-virtual/$', 'main.views.static_page', {'template': 'tour-virtual.html'},name="tour-virtual"),
    url(r'^booking/(?P<id>\d+)/$','main.views.booking',name='booking'),
    url(r'^gallery/$','main.views.gallery',name="gallery"),
    url(r'^gallery/(?P<id>\d+)/$','main.views.galleryinterior',name='galleryinterior'),
    url(r'^show/(?P<slug>\w+)/$','main.views.show', name='show'),
    url(r'^tickets/', 'main.views.tickets', name='tickets'),
    url(r'^cart/', 'main.views.cart', name='cart'),
    url(r'^checkout/', 'main.views.checkout', name='checkout'),   
    url(r'^payment/','main.views.payment',name='payment'),
    url(r'^postpayment/$','main.views.postpayment',name="postpayment"),
    url(r'^timeout/(?P<id>\d+)/$', 'main.views.timeout', name='timeout'), 
    url(r'^delete_cart/', 'main.views.deletecart', name='delete_cart'),   
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^accounts/login/$',  login,{'template_name': 'main/login.html'}, name="login"),
    url(r'^accounts/logout/$', logout, {'next_page': reverse_lazy('login')},name="logout",),
    url(r'^confirm/$','main.views.confirm',name="confirm"), #cambiar cuando se pague
    url(r'^success/$','main.views.success',name="success"),
    url(r'^privacity/$','main.views.static_page', {'template': 'politicas.html'},name="privacity"),
    url(r'^terms/$','main.views.static_page', {'template': 'terminos.html'},name="terms"),
    url(r'^ticket/(?P<id>\d+)/$','main.views.ticket',name="ticket"),
    url(r'^report/$','main.views.report',name="report"),
    url(r'^report2/$','main.views.report2',name="report2"),
    url(r'^report_excel/$','main.views.report_excel',name="report_excel"),
    url(r'^mailing/$','main.views.mailing',name="mailing"),
    url(r'^update-print-status/$','main.views.update_print_status',name="update_print_status"),
#urlpatterns += i18n_patterns('',
    )
