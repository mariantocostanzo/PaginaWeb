from .models import Preguntas, ProgresoSesion, User
import random

#obtener id de pregunta
def obtener_id_disponible(id_usuario):
    usuario = User.objects.get(id=id_usuario)

    sesion = ProgresoSesion.objects.get(usuario=usuario)

    preguntas_disponibles = sesion.preguntas_disponibles.split(",")

    id_random = random.randint(1, len(preguntas_disponibles))
    print(f"preguntas_disponibles: {preguntas_disponibles}")
    print(f"id_disponible: {preguntas_disponibles[id_random - 1]}")

    return preguntas_disponibles[id_random - 1]


def sacar_id_de_lista(id_usuario, id_pregunta):
    usuario = User.objects.get(id=id_usuario)

    sesion = ProgresoSesion.objects.get(usuario=usuario)

    preguntas_disponibles = sesion.preguntas_disponibles.split(",")
    print(preguntas_disponibles)

    id_pregunta = str(id_pregunta)

    preguntas_disponibles.remove(id_pregunta)

    string_preguntas_disponibles = ""

    for id in preguntas_disponibles:
        string_preguntas_disponibles += str(id) + ","
    
    string_preguntas_disponibles = string_preguntas_disponibles[:-1]

    sesion.preguntas_disponibles = string_preguntas_disponibles

    print(string_preguntas_disponibles)

    sesion.save()

#vista que va a mostrar la pregunta:
    #esa pregunta, no va a estar disponible.
    #vamos a generar otra vista, de una pregunta que está disponible