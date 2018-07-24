from django.conf.urls import url

from orders.views import OrderShowView

urlpatterns = [
	url(r'^orders/settlement/', OrderShowView.as_view())
]
