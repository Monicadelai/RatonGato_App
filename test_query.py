import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RatonGato.settings')
django.setup()

from server.models import User, Game, Move

#Compruebe que exite un usuario con id 10, en caso contrario crear el usuario
id=10
username='u10'
password='p10'
u = User.objects.filter(id=id)
if u.exists():
	u10 = User.objects.get(id=id)
else:
	u10 = User(id=id, username=username, password=password)
	u10.save()

#Compruebe si existe un usuario con id=11 en caso contrario crear el usuario
id=11
username='u11'
password='p11'
u = User.objects.filter(id=id)
if u.exists():
	u11 = User.objects.get(id=id)
else:
	u11 = User(id=id, username=username, password=password)
	u11.save()

#Cree un juego asignado al usuario con id=10. El id correspondiente al segundo
#usuario  sera  NULL.  Si  os  hiciera  falta  en  el  futuro,  el  id  del  nuevo  juego  se
#puede obtener como nombre_objeto_juego.id tras persistir el objeto de tipo juego (o equivalente).
id=1
catUser=u10
g = Game.objects.filter(catUser=u10)
if g.exists():
	g1 = g[0]
else:
	g1 = Game(id=id, catUser=catUser)
	g1.save()

#Busque un juego con un solo usuario asignado. Para ellos se puede usar la funcion
#filter con argumento (nombreUser2__isnull=True) donde nombreUSer2 es el atributo
#del nombre de usuario del segundo usuario

#El usuario con id=11 se une al juego encontrado en el paso anterior. Para hacer
#un update de un objeto solo teneis que asignarle los nuevo valores y guardarlo (save())
g = Game.objects.filter(mouseUser__isnull=True)
if g.exists():
	g1 = g[0]
	g1.mouseUser=u11
	g1.save()
else:
	print("No existen juegos sin raton")

#Anadir  un  movimiento  realizado  por  el  usuario  con  id=10.  El  segundo  gato
#pasa  de  2  a  11.  IMPORTANTE:  hay  que  crear  un  movimiento  y  actualizar
#cat 2 y catTurn en la clase Game.
id=1
origin=2
target=11
m = Move.objects.filter(id=id)
if m.exists():
	m1 = Move.objects.get(id=id)
else:
	m1 = Move(id=id, origin=origin, target=target, game=g1)
	m1.save()


g1.cat2=target
g1.catTurn=False
g1.save()

#Anadir un movimiento realizado por el usuario con id=11. El raton pasa de
#59 a 52. IMPORTANTE: hay que crear un movimiento y actualizar
#mouse y catTurn en la clase Game.
id=2
origin=59
target=52
m = Move.objects.filter(id=id)
if m.exists():
	m1 = Move.objects.get(id=id)
else:
	m1 = Move(id=id, origin=origin, target=target, game=g1)
	m1.save()

g1.mouse=52
g1.catTurn=True
g1.save()



