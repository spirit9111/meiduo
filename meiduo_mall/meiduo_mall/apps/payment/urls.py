from django.conf.urls import url

from payment.views import PaymenView, SaveChangeStatusView

urlpatterns = [
	url(r'^orders/(?P<order_id>\d+)/payment/$', PaymenView.as_view()),
	url(r'^payment/status/', SaveChangeStatusView.as_view()),
]
