from django.urls import path
from . import views

urlpatterns = [
	path('editProfile/', views.EditProfileView.as_view()),
	path('myOrders/', views.EditProfileView.as_view()),

]