from django.conf.urls import patterns, include, url
from django.contrib import admin
from contract.views import update_load_data, update_repayment_data

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'btc_cacheserver.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^bc/loan/update/$', update_load_data),
    url(r'^bc/repayment/update/$', update_repayment_data)
)
