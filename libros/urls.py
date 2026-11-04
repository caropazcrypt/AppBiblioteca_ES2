from django.urls import path
from . import views

urlpatterns =[
    path('', views.lista_libros, name = 'lista_libros'),
    path('crear/', views.crear_libro, name= 'crear_libro'),
    path('editar/<int:id>/', views.editar_libro, name = 'editar_libro'),
    path('eliminar/<int:id>/', views.eliminar_libro, name = 'eliminar_libro'),
    path('api/libros/', views.LibrosApiView.as_view(), name='api_libros'),
    path('api/libros/<int:id>/', views.LibroDetalleApiView.as_view(), name='api_libro_detalle'),
]
