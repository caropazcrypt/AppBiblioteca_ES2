from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_libros, name = 'lista_libros'),
    path('crear/', views.crear_libro, name= 'crear_libro'),
    path('editar/<int:id>/', views.editar_libro, name = 'editar_libro'),
    path('eliminar/<int:id>/', views.eliminar_libro, name = 'eliminar_libro'),
    path('login/', views.login_view, name='login'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('logout/', views.logout_view, name='logout'),
]