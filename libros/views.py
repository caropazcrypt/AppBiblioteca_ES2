from django.shortcuts import render, redirect, get_object_or_404
from .models import Libro
from datetime import date
from django.contrib.auth.decorators import login_required

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