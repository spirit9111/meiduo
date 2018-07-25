from django.conf.urls import url

from payment.views import PaymenView

urlpatterns = [
	url(r'^orders/(?P<order_id>\d+)/payment/$', PaymenView.as_view())
]
