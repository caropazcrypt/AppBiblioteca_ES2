from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Libro
from datetime import date, datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

@login_required
def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'libros/lista_libros.html', {'libros': libros})

@login_required
def crear_libro(request):
    if request.method == 'POST':
        titulo = request.POST['titulo'].strip()
        autor = request.POST['autor'].strip()
        isbn = request.POST['isbn'].strip()
        fecha_publicacion = request.POST['fecha_publicacion']
        disponible = 'disponible' in request.POST
        if titulo == '' or autor == '' or isbn == '' or fecha_publicacion == '':
            return render(request, 'libros/crear_libro.html', {
                'error': 'Todos los campos son obligatorios.'
            })
        if len(titulo) > 200:
            return render(request, 'libros/crear_libro.html', {
                'error': 'El título no puede superar los 200 caracteres.'
            })
        if len(autor) > 150:
            return render(request, 'libros/crear_libro.html', {
                'error': 'El autor no puede superar los 150 caracteres.'
            })
        if not any(letra.isalpha() for letra in autor):
            return render(request, 'libros/crear_libro.html', {
                'error': 'El nombre del autor debe contener al menos 1 letra.'
            })
        if not isbn.isdigit():
            return render(request, 'libros/crear_libro.html', {
                'error': 'El ISBN debe contener solo números.'
            })
        if len(isbn) not in [10, 13]:
            return render(request, 'libros/crear_libro.html', {
                'error': 'El ISBN debe tener 10 o 13 dígitos.'
            })
        if Libro.objects.filter(isbn=isbn).exists():
            return render(request, 'libros/crear_libro.html', {
                'error': 'Ya existe un libro registrado con este ISBN.'
            })
        if fecha_publicacion > str(date.today()):
            return render(request, 'libros/crear_libro.html', {
                'error': 'La fecha de publicación no puede ser futura.'
            })
        Libro.objects.create(
            titulo=titulo,
            autor=autor,
            isbn=isbn,
            fecha_publicacion=fecha_publicacion,
            disponible=disponible
        )
        return redirect('lista_libros')
    return render(request, 'libros/crear_libro.html')

@login_required
def editar_libro(request, id):
    libro = Libro.objects.get(id=id)

    if request.method == "POST":
        titulo = request.POST['titulo'].strip()
        autor = request.POST['autor'].strip()
        isbn = request.POST['isbn'].strip()
        fecha_publicacion = request.POST['fecha_publicacion']
        disponible = 'disponible' in request.POST

        if titulo == '' or autor == '' or isbn == '' or fecha_publicacion == '':
            return render(request, 'libros/editar_libro.html', {'libro': libro, 'error': 'Todos los campos son obligatorios.'})

        if len(titulo) > 200:
            return render(request, 'libros/editar_libro.html', {'libro': libro, 'error': 'El título no puede superar los 200 caracteres.'})

        if len(autor) > 150:
            return render(request, 'libros/editar_libro.html', {'libro': libro, 'error': 'El autor no puede superar los 150 caracteres.'})

        if not any(letra.isalpha() for letra in autor):
            return render(request, 'libros/editar_libro.html', {'libro': libro, 'error': 'El nombre del autor debe contener al menos una letra.'})

        if not isbn.isdigit():
            return render(request, 'libros/editar_libro.html', {'libro': libro, 'error': 'El ISBN debe contener solo números.'})

        if len(isbn) not in [10, 13]:
            return render(request, 'libros/editar_libro.html', {'libro': libro, 'error': 'El ISBN debe tener 10 o 13 dígitos.'})

        if Libro.objects.filter(isbn=isbn).exclude(id=libro.id).exists():
            return render(request, 'libros/editar_libro.html', {'libro': libro, 'error': 'Ya existe otro libro registrado con este ISBN.'})

        if fecha_publicacion > str(date.today()):
            return render(request, 'libros/editar_libro.html', {'libro': libro, 'error': 'La fecha de publicación no puede ser futura.'})

        libro.titulo = titulo
        libro.autor = autor
        libro.isbn = isbn
        libro.fecha_publicacion = fecha_publicacion
        libro.disponible = disponible
        libro.save()

        return redirect('lista_libros')

    return render(request, 'libros/editar_libro.html', {'libro': libro})

@login_required
def eliminar_libro(request, id):
    libro = Libro.objects.get(id=id)
    
    if request.method == 'POST':
        libro.delete()
        return redirect('lista_libros')
        
    return render(request, 'libros/eliminar_libro.html', {'libro': libro})

def login_view(request):
    return render(request, 'libros/login.html')

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)
        
def logout_view(request):
    logout(request)
    return redirect('login')

 
class LibrosApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        libros = Libro.objects.all()

        datos = []

        for libro in libros:
            datos.append({
                'id': libro.id,
                'titulo': libro.titulo,
                'autor': libro.autor,
                'isbn': libro.isbn,
                'fecha_publicacion': str(libro.fecha_publicacion),
                'disponible': libro.disponible
            })

        return Response(datos, status=status.HTTP_200_OK)

    def post(self, request):
        titulo = request.data.get('titulo')
        autor = request.data.get('autor')
        isbn = request.data.get('isbn')
        fecha_publicacion = request.data.get('fecha_publicacion')
        disponible = request.data.get('disponible')

        if not titulo or not autor or not isbn or not fecha_publicacion or disponible is None:
            return Response(
                {'error': 'Todos los campos son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(titulo, str) or not isinstance(autor, str):
            return Response(
                {'error': 'El título y el autor deben ser texto.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        titulo = titulo.strip()
        autor = autor.strip()
        isbn = str(isbn).strip()

        if not titulo or len(titulo) > 200:
            return Response(
                {'error': 'El título es obligatorio y no puede superar los 200 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not autor or len(autor) > 150 or not any(letra.isalpha() for letra in autor):
            return Response(
                {'error': 'El autor debe contener letras y no superar los 150 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isbn.isdigit() or len(isbn) not in [10, 13]:
            return Response(
                {'error': 'El ISBN debe contener 10 o 13 dígitos numéricos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Libro.objects.filter(isbn=isbn).exists():
            return Response(
                {'error': 'Ya existe un libro con ese ISBN.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            fecha = datetime.strptime(fecha_publicacion, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response(
                {'error': 'La fecha debe tener el formato AAAA-MM-DD y ser válida.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if fecha > date.today():
            return Response(
                {'error': 'La fecha de publicación no puede ser futura.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(disponible, bool):
            return Response(
                {'error': 'El campo disponible debe ser true o false.'},
                status=status.HTTP_400_BAD_REQUEST
            )

                
        libro = Libro.objects.create(
            titulo=titulo,
            autor=autor,
            isbn=isbn,
            fecha_publicacion=fecha,
            disponible=disponible
        )

        return Response({
            'id': libro.id,
            'titulo': libro.titulo,
            'autor': libro.autor,
            'isbn': libro.isbn,
            'fecha_publicacion': str(libro.fecha_publicacion),
            'disponible': libro.disponible
        }, status=status.HTTP_201_CREATED)

    
class LibroDetalleApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        libro = get_object_or_404(Libro, id=id)

        datos = {
            'id': libro.id,
            'titulo': libro.titulo,
            'autor': libro.autor,
            'isbn': libro.isbn,
            'fecha_publicacion': str(libro.fecha_publicacion),
            'disponible': libro.disponible
        }

        return Response(datos, status=status.HTTP_200_OK)

    def put(self, request, id):
        libro = get_object_or_404(Libro, id=id)

        titulo = request.data.get('titulo')
        autor = request.data.get('autor')
        isbn = request.data.get('isbn')
        fecha_publicacion = request.data.get('fecha_publicacion')
        disponible = request.data.get('disponible')

        if not titulo or not autor or not isbn or not fecha_publicacion or disponible is None:
            return Response(
                {'error': 'Todos los campos son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    
        if not isinstance(titulo, str) or not isinstance(autor, str):
            return Response(
                {'error': 'El título y el autor deben ser texto.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        titulo = titulo.strip()
        autor = autor.strip()
        isbn = str(isbn).strip()

        if not titulo or len(titulo) > 200:
            return Response(
                {'error': 'El título es obligatorio y no puede superar los 200 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not autor or len(autor) > 150 or not any(letra.isalpha() for letra in autor):
            return Response(
                {'error': 'El autor debe contener letras y no superar los 150 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isbn.isdigit() or len(isbn) not in [10, 13]:
            return Response(
                {'error': 'El ISBN debe contener 10 o 13 dígitos numéricos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Libro.objects.filter(isbn=isbn).exclude(id=libro.id).exists():
            return Response(
                {'error': 'Ya existe otro libro con ese ISBN.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha = datetime.strptime(fecha_publicacion, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response(
                {'error': 'La fecha debe tener el formato AAAA-MM-DD y ser válida.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if fecha > date.today():
            return Response(
                {'error': 'La fecha de publicación no puede ser futura.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(disponible, bool):
            return Response(
                {'error': 'El campo disponible debe ser true o false.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        libro.titulo = titulo
        libro.autor = autor
        libro.isbn = isbn
        libro.fecha_publicacion = fecha
        libro.disponible = disponible

        libro.save()

        return Response({
            'id': libro.id,
            'titulo': libro.titulo,
            'autor': libro.autor,
            'isbn': libro.isbn,
            'fecha_publicacion': str(libro.fecha_publicacion),
            'disponible': libro.disponible
        }, status=status.HTTP_200_OK)

    def delete(self, request, id):
        libro = get_object_or_404(Libro, id=id)

        libro.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
