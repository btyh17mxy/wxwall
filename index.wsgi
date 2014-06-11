import sae
from weixinscreen import wsgi

application = sae.create_wsgi_app(wsgi.application)
