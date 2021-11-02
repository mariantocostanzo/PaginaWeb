from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .utils import obtener_id_disponible, sacar_id_de_lista
from .models import Categoria, EstadisticasUsuarios, LoginDetails, PartidasDetails, ProgresoHistorico, User, Preguntas, ProgresoSesion, Respuesta
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse
from django.db import IntegrityError
import random

# Create your views here.

#view de registrar, logear. copiar documentación
def login_view(request):

    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            LoginDetails.objects.create()
            
            return HttpResponseRedirect(reverse("inicio"))
        else:
            return render(request, "quiz/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "quiz/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("inicio"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "quiz/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            estadisticas = EstadisticasUsuarios.objects.get(id=1)
            estadisticas.cantidad_de_usuarios += 1
            estadisticas.save()
            LoginDetails.objects.create()

        except IntegrityError:
            return render(request, "quiz/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("inicio"))
    else:
        return render(request, "quiz/register.html")


#view index
def index_view(request):
    #TODO eliminar sesion
    #usuario = request.user.id
    if request.user.id:
        sesion, created= ProgresoSesion.objects.get_or_create(usuario=request.user)
        sesion.delete()
    return render(request, 'quiz/index.html', {})

    """
    pregunta/1
    variable = random_numero
    pregunta_view(variable):
        es la primera?
            vamos a pregunta_view_random
        se crea un numero random. para lo proxima
        pregunta_view()
    """


"""
sesion.es_valido = bool
sesion.buffer = int

get
sesion.es_valido = True
sesion.buffer = pregunta_actual
sesion.es_valido = False

if not es_valido:
    mostrar la pregunta del buffer

put
sesion.es_valido = True
"""
#La view que muestra la pregunta
@login_required(login_url='/login')
def pregunta_view(request):
    if request.method == 'GET':
        sesion, created = ProgresoSesion.objects.get_or_create(usuario=request.user)

        if sesion.es_valido:
            sesion.es_valido = False
            
            preguntas = Preguntas.objects.all()

            respuestas = Respuesta.objects.all()

            id_pregunta_disponible = obtener_id_disponible(request.user.id)

            if id_pregunta_disponible == '':
                id_pregunta_disponible = sesion.buffer

            sesion.buffer = id_pregunta_disponible

            sesion.save()

            #quitamos pregunta de las preguntas disponibles
            print(f"llamando a la funcion {id_pregunta_disponible}")
            sacar_id_de_lista(request.user.id, id_pregunta_disponible)
            print(f"llamé a la funcion {id_pregunta_disponible}")

            #id_random = random.randint(1, preguntas.count())
            #id_random = pregunta_id

            pregunta = preguntas.get(id=id_pregunta_disponible)

            respuestas_pregunta = respuestas.filter(pregunta=pregunta)

            return render(request, 'quiz/pregunta.html', {
                'categoria': pregunta.categoria,
                'pregunta': pregunta,
                'respuestas': respuestas_pregunta,
                'vidas': range(sesion.vidas)
            })
        else:
            preguntas = Preguntas.objects.all()

            respuestas = Respuesta.objects.all()

            pregunta_id = sesion.buffer

            pregunta = preguntas.get(id=pregunta_id)

            respuestas_pregunta = respuestas.filter(pregunta=pregunta)

            return render(request, 'quiz/pregunta.html', {
                'categoria': pregunta.categoria,
                'pregunta': pregunta,
                'respuestas': respuestas_pregunta,
                'vidas': range(sesion.vidas)
            })


    if request.method == 'POST':
        sesion = ProgresoSesion.objects.get(usuario=request.user)
        sesion.es_valido = True
        sesion.save()

    # si es correcta => redireccionar a view pregunta_view
        id_respuesta = request.POST["respuesta"]

        respuesta = Respuesta.objects.get(id=id_respuesta)

        if respuesta.es_correcta:
            #obtener el nuevo id, random, que no está repetido
            id_pregunta_disponible = obtener_id_disponible(request.user.id)

            #llevar cuenta de puntos de 10 en 10
            sesion = ProgresoSesion.objects.get(usuario=request.user)
            sesion.puntaje += 10
            sesion.save()

            #redireccionar
            if id_pregunta_disponible:
                return redirect('pregunta_view')
            else:
                return redirect('resultado_view', sesion_id=sesion.id)

            #return redirect('pregunta_view', pregunta_id=id_pregunta_disponible)
        else:
        # si es incorrecta => redireccionar a view fin de partida
            sesion = ProgresoSesion.objects.get(usuario=request.user)
            sesion.vidas -=1
            sesion.save()

            if sesion.vidas > 0:
                id_pregunta_disponible = obtener_id_disponible(request.user.id)
                return redirect('pregunta_view')

            else:
                return redirect('resultado_view', sesion_id=sesion.id)



def resultado_view(request, sesion_id):
    if request.method == 'GET':
        #contar partida
        PartidasDetails.objects.create()

        sesion = ProgresoSesion.objects.get(id=sesion_id)
        ganador = True

        puntaje = sesion.puntaje

        #progreso historico
        progreso_historico, create = ProgresoHistorico.objects.get_or_create(usuario=request.user)

        progreso_historico.puntaje_historico += puntaje

        if progreso_historico.mejor_racha < puntaje:
            progreso_historico.mejor_racha = puntaje
        
        progreso_historico.save()

        if sesion.vidas == 0:
            ganador = False

        return render(request, 'quiz/resultado.html', {
            'sesion_id': sesion_id,
            'puntaje': puntaje,
            'ganador': ganador
        })
    if request.method == 'POST':
        """
        if put:
            sesion.delete()
            redirect a preguntas_view
        """
        sesion = ProgresoSesion.objects.get(id=sesion_id)
        sesion.delete()

        return redirect('pregunta_view')

#   metodo get => mostrar pregunta
#   metodo post => elegir la proxima pregunta.
#       funcion auxiliar, logica para llevar la cuenta de preguntas usando el modelo progresosesion.

#view fin de partida y compartir resultados.


#view estadisticas

def estadisticas_view(request):
    estadisticas = ProgresoHistorico.objects.all().order_by('-mejor_racha')[:10]

    return render(request, 'quiz/estadisticas.html', {
        'estadisticas': estadisticas,
    })
