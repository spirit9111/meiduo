from django.conf.urls import url

from orders.views import OrderShowView, SubmitOrderView

urlpatterns = [
	url(r'^orders/settlement/$', OrderShowView.as_view()),
	url(r'^orders/$', SubmitOrderView.as_view()),
]
