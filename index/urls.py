from django.conf.urls import patterns, include, url


urlpatterns = patterns('index.views',
     url(r'^([a-zA-Z]*)/$', 'index', name='index'),
     url(r'^([a-zA-Z]*[^/]\/get_new_msg)', 'get_new_msg', name='msg'),
     url(r'^([a-zA-Z]*\/get_msg_count)', 'get_msg_count', name='msg_count'),
    # url(r'^wxwall/', include('wxwall.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
