from datetime import date, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Libro

def validar_libro(titulo, autor, isbn, fecha_publicacion):
    
    if not isinstance(titulo, str) or not isinstance(autor, str):
        return None, "El título y el autor deben ser texto."

    if not isinstance(isbn, str):
        if isinstance(isbn, int) and not isinstance(isbn, bool):
            isbn = str(isbn)
        else:
            return None, "El ISBN debe ser texto o un número entero."

    titulo = titulo.strip()
    autor = autor.strip()
    isbn = isbn.strip()

    if not titulo or not autor or not isbn or not fecha_publicacion:
        return None, "Todos los campos son obligatorios."

    if len(titulo) > 200:
        return None, "El título no puede superar los 200 caracteres."

    if len(autor) > 150:
        return None, "El autor no puede superar los 150 caracteres."

    if not any(letra.isalpha() for letra in autor):
        return None, "El nombre del autor debe contener al menos una letra."

    if not isbn.isascii() or not isbn.isdigit():
        return None, "El ISBN debe contener solo números."

    if len(isbn) not in (10, 13):
        return None, "El ISBN debe tener 10 o 13 dígitos."

    try:
        fecha = datetime.strptime(
            fecha_publicacion, "%Y-%m-%d"
        ).date()
    except (ValueError, TypeError):
        return None, "La fecha de publicación debe ser válida (AAAA-MM-DD)."

    if fecha > date.today():
        return None, "La fecha de publicación no puede ser futura."

    datos = {
        "titulo": titulo,
        "autor": autor,
        "isbn": isbn,
        "fecha_publicacion": fecha
    }

    return datos, None


def isbn_duplicado(isbn, libro_id=None):
    consulta = Libro.objects.filter(isbn=isbn)

    if libro_id is not None:
        consulta = consulta.exclude(id=libro_id)

    return consulta.exists()


def datos_libro(libro):
    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "isbn": libro.isbn,
        "fecha_publicacion": str(libro.fecha_publicacion),
        "disponible": libro.disponible
    }

@login_required
def lista_libros(request):
    libros = Libro.objects.all()

    return render(request, "libros/lista_libros.html", {
        "libros": libros
    })

@login_required
def crear_libro(request):

    if request.method == "POST":

        titulo = request.POST.get("titulo", "")
        autor = request.POST.get("autor", "")
        isbn = request.POST.get("isbn", "")
        fecha_publicacion = request.POST.get("fecha_publicacion", "")
        disponible = "disponible" in request.POST

        datos, error = validar_libro(
            titulo, autor, isbn, fecha_publicacion
        )

        if error:
            return render(request, "libros/crear_libro.html", {
                "error": error
            })

        if isbn_duplicado(datos["isbn"]):
            return render(request, "libros/crear_libro.html", {
                "error": "Ya existe un libro registrado con este ISBN."
            })

        Libro.objects.create(
            **datos,
            disponible=disponible
        )

        return redirect("lista_libros")

    return render(request, "libros/crear_libro.html")


@login_required
def editar_libro(request, id):

    libro = get_object_or_404(Libro, id=id)

    if request.method == "POST":

        titulo = request.POST.get("titulo", "")
        autor = request.POST.get("autor", "")
        isbn = request.POST.get("isbn", "")
        fecha_publicacion = request.POST.get("fecha_publicacion", "")
        disponible = "disponible" in request.POST

        datos, error = validar_libro(
            titulo, autor, isbn, fecha_publicacion
        )

        if error:
            return render(request, "libros/editar_libro.html", {
                "libro": libro,
                "error": error
            })

        if isbn_duplicado(datos["isbn"], libro.id):
            return render(request, "libros/editar_libro.html", {
                "libro": libro,
                "error": "Ya existe otro libro registrado con este ISBN."
            })

        libro.titulo = datos["titulo"]
        libro.autor = datos["autor"]
        libro.isbn = datos["isbn"]
        libro.fecha_publicacion = datos["fecha_publicacion"]
        libro.disponible = disponible

        libro.save()

        return redirect("lista_libros")

    return render(request, "libros/editar_libro.html", {
        "libro": libro
    })


@login_required
def eliminar_libro(request, id):

    libro = get_object_or_404(Libro, id=id)

    if request.method == "POST":
        libro.delete()
        return redirect("lista_libros")

    return render(request, "libros/eliminar_libro.html", {
        "libro": libro
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect("lista_libros")

    return render(request, "libros/login.html")


class LoginAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        if not isinstance(username, str) or not isinstance(password, str):
            return Response({
                "error": "Usuario y contraseña son obligatorios."
            }, status=status.HTTP_400_BAD_REQUEST)

        usuario = authenticate(
            username=username,
            password=password
        )

        if usuario is not None:

            login(request, usuario)

            token, creado = Token.objects.get_or_create(
                user=usuario
            )

            return Response({
                "token": token.key
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Credenciales incorrectas"
        }, status=status.HTTP_401_UNAUTHORIZED)


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


class LibrosApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        libros = Libro.objects.all()

        datos = []

        for libro in libros:
            datos.append(datos_libro(libro))

        return Response(
            datos,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        titulo = request.data.get("titulo")
        autor = request.data.get("autor")
        isbn = request.data.get("isbn")
        fecha_publicacion = request.data.get("fecha_publicacion")
        disponible = request.data.get("disponible")

        datos, error = validar_libro(
            titulo, autor, isbn, fecha_publicacion
        )

        if error:
            return Response({
                "error": error
            }, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(disponible, bool):
            return Response({
                "error": "El campo disponible debe ser true o false."
            }, status=status.HTTP_400_BAD_REQUEST)

        if isbn_duplicado(datos["isbn"]):
            return Response({
                "error": "Ya existe un libro registrado con este ISBN."
            }, status=status.HTTP_400_BAD_REQUEST)

        libro = Libro.objects.create(
            **datos,
            disponible=disponible
        )

        return Response(
            datos_libro(libro),
            status=status.HTTP_201_CREATED
        )

class LibroDetalleApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):

        libro = get_object_or_404(Libro, id=id)

        return Response(
            datos_libro(libro),
            status=status.HTTP_200_OK
        )

    def put(self, request, id):

        libro = get_object_or_404(Libro, id=id)

        titulo = request.data.get("titulo")
        autor = request.data.get("autor")
        isbn = request.data.get("isbn")
        fecha_publicacion = request.data.get("fecha_publicacion")
        disponible = request.data.get("disponible")

        datos, error = validar_libro(
            titulo, autor, isbn, fecha_publicacion
        )

        if error:
            return Response({
                "error": error
            }, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(disponible, bool):
            return Response({
                "error": "El campo disponible debe ser true o false."
            }, status=status.HTTP_400_BAD_REQUEST)

        if isbn_duplicado(datos["isbn"], libro.id):
            return Response({
                "error": "Ya existe otro libro registrado con este ISBN."
            }, status=status.HTTP_400_BAD_REQUEST)

        libro.titulo = datos["titulo"]
        libro.autor = datos["autor"]
        libro.isbn = datos["isbn"]
        libro.fecha_publicacion = datos["fecha_publicacion"]
        libro.disponible = disponible

        libro.save()

        return Response(
            datos_libro(libro),
            status=status.HTTP_200_OK
        )

    def delete(self, request, id):

        libro = get_object_or_404(Libro, id=id)

        libro.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
