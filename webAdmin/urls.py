from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from webAdmin import views

app_name = 'webAdmin'

urlpatterns = [

	# path('', views.IndexView.as_view(), name='index'),
	path('homepage/', views.RestaurantListView.as_view(), name='restaruantList'),
	path('restaurant_info/', views.restaurantDetails),

	path('', RedirectView.as_view(url='/accounts/admin_login'), name='accounts'),
	path('accounts/', include('accounts.urls'), name='accounts'),
	path('accept/<int:id>/', views.requestAccept),
	path('database/', admin.site.urls, name='dbadmin'),

]
