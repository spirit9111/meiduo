from django.conf.urls import url
from .views import CartView, CartSelectAllView

urlpatterns = [
	url(r'^cart/$', CartView.as_view()),
	url(r'^cart/selection/', CartSelectAllView.as_view()),
	# url(r'^cart/selection/', CartSelectAllView.as_view()),
]
