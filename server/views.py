from django.http import HttpResponse

from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse, HttpResponseRedirect

from server.forms import UserForm, MoveForm

from models import User, Game, Counter, Move


#variable global
amIcat=""
winner=""
cat_mouse = ""

# index
# Argumentos de entrada: request
# Funcion: Pagina principal

# Autor: Fernando Barroso

def index(request):
    context_dict = {}

    if request.user.is_authenticated():
        user = request.user.username
        context_dict['username'] = user

        
    return render(request, 'server/index.html', context_dict)

# login_user
# Argumentos de entrada: request
# Funcion: Usando el sistema de verificacion de Django, comprueba que el usuario y la clave son correctos
# Autor: Monica de la Iglesia

def login_user(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')
        cat_or_mouse = request.POST.get('cat_or_mouse') #cat - mouse
        global cat_mouse
        cat_mouse = cat_or_mouse

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                request.session['userId'] = user.id
                if cat_or_mouse == "cat":
                    request.session['amIcat']=True
                    amIcat=True
                    create_game(request)
                    return HttpResponseRedirect('/server/join_game/')

                else:
                    request.session['amIcat']=False
                    amIcat=False
                    return HttpResponseRedirect('/server/join_game/')
            else:
                # An inactive account was used - no logging in!
                #return HttpResponse("Your RatonGato account is disabled.")
                return render(request,
                'server/login.html',
                {'error': "Your RatonGato account is disabled."} )
        else:
            # Bad login details were provided. So we can't log the user in.
            #print "Invalid login details: {0}, {1}".format(username, password)
            #return HttpResponse("Invalid login details supplied.")
            return render(request,
            'server/login.html',
            {'error': "Invalid login details supplied."} )

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        context_dict = {'logout_user': "server/logout_user.html"}
        return render(request, 'server/login.html', context_dict)

# logout_user
# Argumentos de entrada: request
# Funcion: Desconexion del usuario
# Autor: Monica de la Iglesia

def logout_user(request):
    
    user = None
    if request.user.is_authenticated():
        user = request.user.username
    # Since we know the user is logged in, we can now just log them out.
        logout(request)
        request.session["countSession"] = 0

    # Take the user back to the homepage.
        return render(request, 'server/logout.html', {'username' : user})
    else:
        return HttpResponse("You are not logged")

# register_user
# Argumentos de entrada: request
# Funcion: Formulario de registro
# Autor: Fernando Barroso

def register_user(request):

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False
    error = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm
        user_form = UserForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            error = True
            return render(request,
            'server/register.html',
            {'error': error} )

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    # Render the template depending on the context.
    if registered:
        return render(request,
            'server/login.html',
            {} )
    else:
        return render(request,
                'server/register.html',
                {'user_form': user_form, 'registered': registered} )

# create_game
# Argumentos de entrada: request
# Funcion: Crea y persiste un juego si el usuario esta logueado
# Autor: Monica de la Iglesia

def create_game(request):
    #comprobamos si el usuario esta autentificado
    if request.user.is_authenticated():

        #si es asi, creamos un juego asignandole el usuario al catUser, poniendo el turno de este a true y guardamos el nuevo juego
        user = User.objects.filter(username = request.user.username)[0] 
        game = Game(catUser=user)
        game.catTurn = True
        game.save()

        #guardamos en nuetro array de sesion las variables amIcat y el id del juego
        request.session["amIcat"] = True
        request.session["gameID"] = game.id
        
        #mostramos la pagina game.html diciendo que se ha creado un juego
        return render(request, 'server/game.html', {'game':game, 'user':user})
    
    #mostramos la pagina nologged.html
    else:
        return render(request, 'server/nologged.html', {})

# counter
# Argumentos de entrada: request
# Funcion: Devuelve dos contadores con el numero de veces que ha llamado a la funcion
# Autor: Fernando Barroso

def counter(request):
    
    contador = Counter.objects.all()
    
    #Condiciones para el contador local
    #si en el array de sesion ya exite la variable 'countSession' sumamos uno al contador
    if "countSession" in request.session:
        request.session["countSession"] += 1
    
    #si en el array de sesion no exite la variable 'countSession', la creamos e inicializamos a 1
    else:
        request.session["countSession"] = 1

    #Condiciones para el contador global
    #si exite alguna tabla contador
    if contador.exists():

        #Sumamos uno a la variable 'countGlobal' y guardamos la modificacion
        contador = contador[0]
        contador.countGlobal += 1
        contador.save()
    
    else:
        #Inicializamos la Tabla contador con la variable 'countGlobal' a 1
        contador = Counter(countGlobal = 1)
        contador.save()

    #Mostramos la pagina counter.html pasandole la informacion actualizada de los contadores
    return render(request, 'server/counter.html', {'counterSes': request.session["countSession"], 'counterGlobal': contador.countGlobal})

# status_turn
# Argumentos de entrada: request
# Funcion: Elimina las partidas creadas por el usuario logueado
# Autor: Monica de la Iglesia

def clean_orphan_games(request):

    #Busca todos los juego que tiene un solo usuario asignado (mouseUSer=NULL)
    game = Game.objects.filter(catUser__isnull = False, mouseUser__isnull = True)
    
    #si no existe ningun juego con un solo usuario asignado
    if not game.exists():
        context_dict = {'rows_count': 0}
        #Mostramos las pagina clean.html pasandole que no ha encontrado ningun juego que borrar
        return render(request, 'server/clean.html', context_dict)
        
    else:
        #Borramos todos los juegos encontrados
        rows = len(game)
        game.delete()
        context_dict = {'rows_count': rows}
        #Mostramos las pagina clean.html pasandole la cantidad de juegos que han sido borrados
        return render(request, 'server/clean.html', context_dict)

# status_turn
# Argumentos de entrada: request
# Funcion: Consulta de quien es el turno
# Autor: Fernando Barroso


def status_turn2(request):
    #comprobamos si el usuario esta autentificado
    if request.user.is_authenticated():
        #Si existe una variable 'gameID' en el array session  
        if "gameID" in request.session: 
            gameID = request.session["gameID"]
            #Buscamo el juego con ese id
            games = Game.objects.filter(id=gameID)
            #si existe el juego
            if games.exists():
                game = games[0]
                
                #Si el 'catTurn' es true y el usuario loggeado es un gato o si el 'catTurn' es false y el usuario loggeado no es un gato 
                if (game.catTurn==True and request.session["amIcat"] == True) or (game.catTurn==False and request.session["amIcat"] == False):
                    context_dict = {'myTurn' : True}
                                    
                    #Mostramos la pagina turn.htm pasandole como argumento True
                    return render(request, 'server/turn.html', context_dict)
            
                #en caso contrario
                else:
                    context_dict = {'myTurn' : False}
                    #Mostramos la pagina turn.htm pasandole como argumento false
                    return render(request, 'server/turn.html', context_dict)

            #Si no existe ningun juego con ese identificador  
            else:
                context_dict = {'myTurn' : False}
                #Mostramos la pagina turn.htm pasandole como argumento false
                return render(request, 'server/turn.html', context_dict)

        #Si en en array session no existe una variable 'gameID'
        else:
            context_dict = {'myTurn' : False}
            #Mostramos la pagina turn.htm pasandole como argumento false
            return render(request, 'server/turn.html', context_dict)

    #Si el usuario no esta loggeado
    else:
        #Mostramos la pagina nologged.html
        return render(request, 'server/nologged.html', {})


def status_turn(request):

    #comprobamos si el usuario esta autentificado
    if request.user.is_authenticated():
        
        #Si existe una variable 'gameID' en el array session  
        if "gameID" in request.session: 
            gameID = request.session["gameID"]
            #Buscamo el juego con ese id
            games = Game.objects.filter(id=gameID)
            
            #si existe el juego
            if games.exists():
                game = games[0]
                
                #Si el 'catTurn' es true y el usuario loggeado es un gato o si el 'catTurn' es false y el usuario loggeado no es un gato 
                if (game.catTurn==True and request.session["amIcat"] == True) or (game.catTurn==False and request.session["amIcat"] == False):
                    context_dict = {'myTurn' : True}                    
                    #Mostramos la pagina turn.htm pasandole como argumento True
                    #return render(request, 'server/turn.html', context_dict)
            
                #en caso contrario
                else:
                    context_dict = {'myTurn' : False}
                    #Mostramos la pagina turn.htm pasandole como argumento false
                    #return render(request, 'server/turn.html', context_dict)

            #Si no existe ningun juego con ese identificador  
            else:
                context_dict = {'myTurn' : False}
                #Mostramos la pagina turn.htm pasandole como argumento false
                #return render(request, 'server/turn.html', context_dict)

        #Si en en array session no existe una variable 'gameID'
        else:
            context_dict = {'myTurn' : False}
            #Mostramos la pagina turn.htm pasandole como argumento false
            #return render(request, 'server/turn.html', context_dict)
        return context_dict 
    #Si el usuario no esta loggeado
    else:
        #Mostramos la pagina nologged.html
        return render(request, 'server/nologged.html', {})

# status_board
# Argumentos de entrada: request
# Funcion: Estado del tablero
# Autor: Monica de la Iglesia

def status_board(request):
    
    #Comprobamos si es usuario esta loggeado
    if request.user.is_authenticated():

        if request.is_ajax():
            template = "server/game_ajax.html"
        else:
            template = "server/game.html"

        context_dict={}
        #Si existe la variable 'gameID' en el array session

        if "gameID" in request.session: 
            gameID = request.session["gameID"]
            #buscamos un juego con el identificador encontrado en el array session
            games = Game.objects.filter(id = gameID)
            
            #Si existe el juego buscado
            if games.exists():
                game = games[0]
                #inicializamos una lista de 64 posiciones
                context_dict['board'] = list(range(0, 64))

                #Inicializamos todas las posiciones de esa lista a 0
                for i in range(64):
                    context_dict['board'][i] = 0
            
                #Modificamos poniendo a 1 las casillas en las que se encuentran los gatos, y a -1 la casilla en la que esta el raton
                context_dict['board'][game.cat1] = 1
                context_dict['board'][game.cat2] = 1
                context_dict['board'][game.cat3] = 1
                context_dict['board'][game.cat4] = 1
                context_dict['board'][game.mouse] = -1

                if game.mouseUser is None:
                    context_dict['myTurn']="Esperando un usuario Raton"
                    return render(request, template, context_dict)
        
                #Mostramos la pagina board.html pasandole como argumento es array con el estado del tablero
                return_dict=status_turn(request)
                if return_dict['myTurn'] == True:
                    context_dict['myTurn'] = "Mueve, es tu turno"
                else:
                    context_dict['myTurn'] = "Te toca esperar, es el turno de tu oponente"
                
                return render(request, template, context_dict)
        else:
            #mira a ver si se puede unir a alguna partida
            join_game(request)
            if "gameID" in request.session: 
                gameID = request.session["gameID"]
                #buscamos un juego con el identificador encontrado en el array session
                games = Game.objects.filter(id = gameID)
                
                #Si existe el juego buscado
                if games.exists():
                    game = games[0]
                    #inicializamos una lista de 64 posiciones
                    context_dict['board'] = list(range(0, 64))

                    #Inicializamos todas las posiciones de esa lista a 0
                    for i in range(64):
                        context_dict['board'][i] = 0
                
                    #Modificamos poniendo a 1 las casillas en las que se encuentran los gatos, y a -1 la casilla en la que esta el raton
                    context_dict['board'][game.cat1] = 1
                    context_dict['board'][game.cat2] = 1
                    context_dict['board'][game.cat3] = 1
                    context_dict['board'][game.cat4] = 1
                    context_dict['board'][game.mouse] = -1
            
                    #Mostramos la pagina board.html pasandole como argumento es array con el estado del tablero
                    return_dict=status_turn(request)
                    if return_dict['myTurn'] == True:
                        context_dict['myTurn'] = "Mueve, es tu turno"
                    else:
                        context_dict['myTurn'] = "Te toca esperar, es el turno de tu oponente"

                    return render(request, template, context_dict)
            else:
                context_dict['myTurn']="Esperando que se cree un juego"
                return render(request, template, context_dict)
            #print "llega else"
            #context_dict['myTurn'] = return_dict['myTurn']
            #print "pasa context_dict"
            #return render(request, template, context_dict)

        #Mostramos la pagina board.html pasandole como argumento es array con el estado del tablero
        return render(request, template, context_dict)

    #Si el usuario no esta loggeado
    else:
        #Mostramos la pagina nologged.html
        return render(request, 'server/nologged.html', {})

# join_move
# Argumentos de entrada: request
# Funcion: Busca el ultimo juego con un solo usuario asignado y se le asigna al usuario logeado como usuario raton
# Autor: Monica de la Iglesia

def join_game(request): 

    #Comprobamos si el usuario es gato
    if request.session['amIcat'] == True:
        return render(request, 'server/game.html', {})

    #si es raton
    else:
        #Buscamos el usuario loggeado filtrando todos los usarios por la varibale 'userId' de la session
        user = User.objects.get(id = request.session['userId'])
        #Buscamos todos los juegos que que no tienen usuario raton y los ordenamos en orden decreciente segun el id
        games = Game.objects.filter(mouseUser__isnull=True).order_by("-id")

        #Si existen juegos, nos  quedamos con el primero, es decir, con el del identificador mayor y le asiganos el usuario al raton
        if games.exists():
            thereIsGame = True
            game = games[0]
            game.mouseUser=user
            #Guardamos los cambios realizados en el juego
            game.save()
            #Actualizamos el array session guardando el id del juego, y 'amIcat' a false
            request.session["gameID"] = game.id
            #request.session["amIcat"] = False

            #Mostramos la pagina join.html pasandole como argumento la variable 'thereIsGame' que en este caso vale true, y el juego
            return render(request, 'server/game.html',{})

        #si no existen juegos
        else:
            thereIsGame = False
            #Mostramos la pagina join.html pasandole como argumento la variable 'thereIsGame' que en este caso vale False, y el juego
            return render(request, 'server/game.html', {})

    #Si no esta loggeado mostramos la pagina nologged.html   
    #else:
    #    return render(request, 'server/nologged.html', {})

# mouse_move
# Argumentos de entrada: request, destino, gameID
# Funcion: Movimiento del raton en el tablero
# Autor: Fernando Barroso

def mouse_move(request, destino, gameID):
    context_dict = {}
    #Buscamos el juego con el id que nos han pasado por parametro
    games = Game.objects.filter(id = gameID)
    
    #Si el juego existe
    if games.exists():
        game = games[0]
          
        #Comprobamos si es el turno del raton
        if (game.catTurn == False):
            #Comprobamos si el destino al que vamos se corresponde con la posicion de un gato
            if ((destino != game.cat1) and (destino != game.cat2) and (destino != game.cat3) and (destino != game.cat4)):
                #Comprobamos que el movimiento que va a realizar el raton es el correcto
                if((destino == game.mouse - 9) or (destino == game.mouse - 7) or (destino == game.mouse + 9) or (destino == game.mouse + 7)):
                    #Comprobamos que el movimiento a realizar se hace dentro del tablero
                    if ((destino >= 0) and (destino < 64)):
                        #Comprobamos si el raton esta en el borde de la derecha del tablero
                        if game.mouse % 8 == 7:
                            #Comprobamos que el movimiento no se salga del tablero
                            if ((destino == game.mouse + 7) or (destino == game.mouse - 9)):
                                move = Move(origin = game.mouse, target = destino, game = game)
                                game.mouse = move.target
                                game.catTurn = True
                                move.save()
                                game.save()
                                #Guardamos el movimiento y tambien la pueva posicion del raton
                                context_dict['Created'] = True
                                context_dict['Move'] = move
                                context_dict['Game'] = game 
                            
                            else: 
                                context_dict['Error'] = 'Cannot create a move'
                                context_dict['Created'] = False
                                context_dict['Move'] = None
                                context_dict['Game'] = None
                        #Comprobamos si el raton esta en el borde de la izquierda del tablero
                        elif game.mouse % 8 == 0:
                            #Comprobamos que el movimiento del raton no se salga del tablero
                            if ((destino == game.mouse + 9) or (destino == game.mouse - 7)):
                                move = Move(origin = game.mouse, target = destino, game = game)
                                game.mouse = move.target
                                game.catTurn = True
                                move.save()
                                game.save()
                                #Guardamos el movimiento y tambien la pueva posicion del raton
                                context_dict['Created'] = True
                                context_dict['Move'] = move
                                context_dict['Game'] = game 
                           
                            #Si el movimiento del raton se sale del tablero
                            else: 
                                context_dict['Error'] = 'Cannot create a move'
                                context_dict['Created'] = False
                                context_dict['Move'] = None
                                context_dict['Game'] = None

                        #Este movimiento se crea debido a que no se encuentra en ninguna situacion anterior
                        else:
                            move = Move(origin = game.mouse, target = destino, game = game)
                            game.mouse = move.target
                            game.catTurn = True
                            move.save()
                            game.save()
                            #Guardamos el movimiento y tambien la pueva posicion del raton
                            context_dict['Created'] = True
                            context_dict['Move'] = move
                            context_dict['Game'] = game 
               
                    #El movimiento a realizar no se hace dentro del tablero
                    else:
                        context_dict['Error'] = 'Cannot create a move'
                        context_dict['Created'] = False
                        context_dict['Move'] = None
                        context_dict['Game'] = None

                #El movimiento que va a realizar el raton es incorrecto
                else:
                    context_dict['Error'] = 'Cannot create a move'
                    context_dict['Created'] = False
                    context_dict['Move'] = None
                    context_dict['Game'] = None
            
            #Al destino al que vamos esta ocupado por un gato
            else:
                context_dict['Error'] = 'cannot be a cat in the target'
                context_dict['Created'] = False
                context_dict['Move'] = None
                context_dict['Game'] = None

        #No es el turno del raton
        else:
            context_dict['Error'] = 'Cannot create a move'
            context_dict['Created'] = False
            context_dict['Move'] = None
            context_dict['Game'] = None

    #No existe ningun juego con ese identificador
    else:
        context_dict['Error'] = 'Cannot create a move'
        context_dict['Created'] = False
        context_dict['Move'] = None
        context_dict['Game'] = None

    return context_dict

# cat_move
# Argumentos de entrada: request, origen, destino, gameID
# Funcion: Movimiento de un gato en el tablero
# Autor: Fernando Barroso

def cat_move(request, origen, destino, gameID):
    context_dict = {}
    #Buscamos el juego con el id que nos han pasado por parametro
    games = Game.objects.filter(id=gameID)
    
    #Si el juego existe
    if games.exists():
        game = games[0]

        #Comprobamos si es el turno del gato
        if (game.catTurn == True):
            #Comprobamos que el origen se corresponda con ningun otro gato ni con ningun raton
            if ((game.cat1 == origen) or (game.cat2 == origen) or (game.cat3 == origen) or (game.cat4 == origen)):
                if((game.cat1 != destino) and (game.cat2 != destino) and (game.cat3 != destino) and (game.cat4 != destino) and (game.mouse != destino)):
                    #Comprobamos que el movimiento que va a realizar el gato es correcto
                    if ((destino < 64) and (destino > origen)):
                        #Comprobamos que el destino es correcto
                        if ((destino == origen + 9) or (destino == origen + 7)):
                            #Comprobamos si el origen esta en el borde de la izquierda del tablero
                            if (origen % 8 == 0):
                                #Comprobamos que el movimiento del gato sea de la manera correcta
                                if (destino == origen + 9):
                                    move = Move (origin = origen, target = destino, game = game)
                                    if (game.cat1 == origen):
                                        game.cat1 = move.target
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game

                                    elif (game.cat2 == origen):
                                        game.cat2 = move.target
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game

                                    elif (game.cat3 == origen):
                                        game.cat3 = move.target
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game

                                    elif (game.cat4 == origen):
                                        game.cat4 = move.target
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game
                            
                                    else:
                                        context_dict['Error'] = 'Cannot create a move'
                                        context_dict['Created'] = False
                                        context_dict['Move'] = None
                                        context_dict['Game'] = None
                                else:
                                    context_dict['Error'] = 'Cannot create a move'
                                    context_dict['Created'] = False
                                    context_dict['Move'] = None
                                    context_dict['Game'] = None 

                            #Comprobamos si el origen esta en el borde de la derecha del tablero
                            elif (origen % 8 == 7):
                                #Comprobamos que el movimiento del gato sea de la manera correcta
                                if (destino == origen + 7):
                                    move = Move (origin = origen, target = destino, game = game)
                                    if (game.cat1 == origen):
                                        game.cat1 = move.target
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game

                                    elif (game.cat2 == origen):
                                        game.cat2 = move.target
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game

                                    elif (game.cat3 == origen):
                                        game.cat3 = move.target
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game

                                    elif (game.cat4 == origen):
                                        game.cat4 = move.target
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game

                                    else:
                                        game.catTurn = False
                                        move.save()
                                        game.save()
                                        #Guardamos el movimiento y tambien la pueva posicion del gato
                                        context_dict['Created'] = True
                                        context_dict['Move'] = move
                                        context_dict['Game'] = game
                             
                                else:
                                    context_dict['Error'] = 'Cannot create a move'
                                    context_dict['Created'] = False
                                    context_dict['Move'] = None
                                    context_dict['Game'] = None

                            #Este movimiento se crea debido a que no se encuentra en ninguna situacion anterior.
                            else:
                                move = Move (origin = origen, target = destino, game = game)
                                if (game.cat1 == origen):
                                    game.cat1 = move.target
                                    game.catTurn = False
                                    move.save()
                                    game.save()
                                    #Guardamos el movimiento y tambien la pueva posicion del gato
                                    context_dict['Created'] = True
                                    context_dict['Move'] = move
                                    context_dict['Game'] = game

                                elif (game.cat2 == origen):
                                    game.cat2 = move.target
                                    game.catTurn = False
                                    move.save()
                                    game.save()
                                    #Guardamos el movimiento y tambien la pueva posicion del gato
                                    context_dict['Created'] = True
                                    context_dict['Move'] = move
                                    context_dict['Game'] = game

                                elif (game.cat3 == origen):
                                    game.cat3 = move.target
                                    game.catTurn = False
                                    move.save()
                                    game.save()
                                    #Guardamos el movimiento y tambien la pueva posicion del gato
                                    context_dict['Created'] = True
                                    context_dict['Move'] = move
                                    context_dict['Game'] = game

                                elif (game.cat4 == origen):
                                    game.cat4 = move.target
                                    game.catTurn = False
                                    move.save()
                                    game.save()
                                    #Guardamos el movimiento y tambien la pueva posicion del gato
                                    context_dict['Created'] = True
                                    context_dict['Move'] = move
                                    context_dict['Game'] = game

                                else:
                                    context_dict['Error'] = 'Cannot create a move'
                                    context_dict['Created'] = False
                                    context_dict['Move'] = None
                                    context_dict['Game'] = None
                        #El destino se no esta dentro del tablero
                        else:
                            context_dict['Error'] = 'Cannot create a move'
                            context_dict['Created'] = False
                            context_dict['Move'] = None
                            context_dict['Game'] = None

                    #El movimiento que va a realizar es incorrecto
                    else:
                        context_dict['Error'] = 'you must move to a contiguous diagonal place'
                        context_dict['Created'] = False
                        context_dict['Move'] = None
                        context_dict['Game'] = None
                #El destino se corresponde con la posicion de algun gato o raton
                else:
                    context_dict['Error'] = 'cannot be a cat in the target'
                    context_dict['Created'] = False
                    context_dict['Move'] = None
                    context_dict['Game'] = None
            #El origen no se corresponde con la posicion de algun gato o raton
            else:
                context_dict['Error'] = 'Cannot create a move'
                context_dict['Created'] = False
                context_dict['Move'] = None
                context_dict['Game'] = None

        #No es el turno del gato
        else:
            context_dict['Error'] = 'Cannot create a move'
            context_dict['Created'] = False
            context_dict['Move'] = None
            context_dict['Game'] = None
    
    #No hay ningun juego con ese id
    else:
        context_dict['Error'] = 'Cannot create a move'
        context_dict['Created'] = False
        context_dict['Move'] = None
        context_dict['Game'] = None

    return context_dict

# move
# Argumentos de entrada:
# Funcion: Esta funcion llama a mouse_move o cat_move dependiendo de a quien le toque jugar
# Autor: Monica de la Iglesia

def move(request):
    context_dict = {}
    return_dict = {}
    #Comprobamos que el usuario esta loggeado
    if request.user.is_authenticated():

        if request.method == 'POST':
            move_form = MoveForm(request.POST)
      
            # Comprueba que el formulario es correcto.
            if move_form.is_valid:
                origen = int(request.POST.get('origin'))
                destino = int(request.POST.get('target'))

                #Si existe la variable 'gameID' en el array session
                if "gameID" in request.session: 
                    if "amIcat" in request.session:
                        gameID = request.session['gameID']
                        amIcat = request.session['amIcat']
                        games = Game.objects.filter(id=gameID)
			
                        #si el juego existe
                        if games.exists():
                            game = games[0]
                            #si el juego tiene usuario raton
                            if game.mouseUser is not None:
                                #si el usuario loggeado es un gato
                                if(amIcat == True):
                                    #si es el turno del gato
                                    if(game.catTurn == True):
                                        return_dict = cat_move(request, origen, destino, gameID)
                                    else:
                                        context_dict["error"] = "Cannot create a move"
                                        return render(request, 'server/move.html', context_dict)
                                #si el usuario loggeado es un raton
                                else:
                                    #si es el turno del raton
                                    if(game.catTurn == False):
                                        return_dict = mouse_move(request, destino, gameID)
                                    else:
                                        context_dict["error"] = "Cannot create a move"
                                        return render(request, 'server/move.html', context_dict)
                            #Si el juego no tiene usuario raton
                            else:
                                context_dict["error"] = "Cannot create a move: A valid game requires a mouse user"
                                return render(request, 'server/move.html', context_dict)

                            #Si el juego esta creado 
                            if "Created" in return_dict:
                                context_dict['moveDone'] = return_dict['Created']
                            else:
                                context_dict['moveDone'] = False

                            if context_dict['moveDone'] == True:
                                context_dict['move'] = return_dict['Move'] 
                                context_dict['game'] = return_dict['Game']
                                
                            elif "Error" in return_dict:
                                context_dict["error"] = return_dict['Error']
                                return render(request, 'server/move.html', context_dict) 

                            context_dict["move_form"] = move_form

                        #si el juego no existe
                        else:
                            context_dict['error'] = 'No estas en una partida'
                #si no esta va la variable 'gameID'
                else:            
                    context_dict['error'] = 'No estas en una partida'

            
            
            #si el movimiento no es valido
            else:
                print moveform.errors
 
        else:
            moveform = MoveForm()
            context_dict["move_form"] = moveform
 
        # Devuelve el template de move
        # return_dict = winner (request)
        # if return_dict['final_partida'] == True :
        #     context_dict['final_partida'] = return_dict['final_partida']
        #     context_dict['terminada'] = "terminada"
        #     context_dict['ganador'] = return_dict['winner']
        #     print "******************************GANADOR*****************\n"
        #     return render(request, 'server/winner.html', context_dict)

        return render(request, 'server/move.html', context_dict)



    #Si no esta loggeado mostramos la pagina nologged.html   
    else:
        return render(request, 'server/nologged.html', {})


def winner(request):

    if "gameID" in request.session: 
        gameID = request.session['gameID']
        amIcat = request.session['amIcat']
        games = Game.objects.filter(id=gameID)

        #si el juego existe
        if games.exists():

            game = games[0]
            gato1=game.cat1
            gato2=game.cat2
            gato3=game.cat3
            gato4=game.cat4
            mouse=game.mouse

            context_dict= {}
            context_dict['amIcat'] = amIcat
            context_dict['final_partida'] = False

            if mouse<7:
                context_dict["winner"] = "raton"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = False
                return render(request, 'server/winner.html', context_dict)
            elif (mouse>=8 and mouse<=15) and (gato1>=8) and (gato2>=8) and (gato3>=8) and (gato4>=8):
                context_dict["winner"] = "raton"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = False
                return render(request, 'server/winner.html', context_dict)
            elif (mouse>=16 and mouse<=23) and (gato1>=16) and (gato2>=16) and (gato3>=16) and (gato4>=16):
                context_dict["winner"] = "raton"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = False
                return render(request, 'server/winner.html', context_dict)
            elif (mouse>=24 and mouse<=31) and (gato1>=24) and (gato2>=24) and (gato3>=24) and (gato4>=24):
                context_dict["winner"]= "raton"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = False
                return render(request, 'server/winner.html', context_dict)
            elif (mouse>=32 and mouse<=39) and (gato1>=32) and (gato2>=32) and (gato3>=32) and (gato4>=32):
                context_dict["winner"] = "raton"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = False
                return render(request, 'server/winner.html', context_dict)
            elif (mouse>=40 and mouse<=47) and (gato1>=40) and (gato2>=40) and (gato3>=40) and (gato4>=40):
                context_dict["winner"] = "raton"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = False
                return render(request, 'server/winner.html', context_dict)
            elif (mouse>=48 and mouse<=55) and (gato1>=48) and (gato2>=48) and (gato3>=48) and (gato4>=48):
                context_dict["winner"] = "raton"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = False
                return render(request, 'server/winner.html', context_dict)
            elif (mouse>=56 and mouse<=63) and (gato1>=56) and (gato2>=56) and (gato3>=56) and (gato4>=56):
                context_dict["winner"] = "raton"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = False
                return render(request, 'server/winner.html', context_dict)
            #raton acorralado en el borde izq del tablero 
            elif ((mouse % 8 == 0) and (mouse>=8) and (mouse<=48) and (gato1==mouse-7 or gato2==mouse-7 or gato3==mouse-7 or gato4==mouse-7)
                    and (gato1==mouse+9 or gato2==mouse+9 or gato3==mouse+9 or gato4==mouse+9)):
                context_dict["winner"] = "gato"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = True
                return render(request, 'server/winner.html', context_dict)
            #raton acorralado en el borde derecho del tablero
            elif ((mouse % 8 == 7) and (mouse>=15) and (mouse<=55) and (gato1==mouse-9 or gato2==mouse-9 or gato3==mouse-9 or gato4==mouse-9)
                    and (gato1==mouse+7 or gato2==mouse+7 or gato3==mouse+7 or gato4==mouse+7)):
                context_dict["winner"] = "gato"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = True
                return render(request, 'server/winner.html', context_dict)
            #raton acorralado en mitad del tablero
            elif ((gato1==mouse-9 or gato2==mouse-9 or gato3==mouse-9 or gato4==mouse-9) and (gato1==mouse-7 or gato2==mouse-7 or gato3==mouse-7 or gato4==mouse-7)
                    and (gato1==mouse+7 or gato2==mouse+7 or gato3==mouse+7 or gato4==mouse+7) and (gato1==mouse+9 or gato2==mouse+9 or gato3==mouse+9 or gato4==mouse+9)):
                context_dict["winner"] = "gato"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = True
                return render(request, 'server/winner.html', context_dict)
            #raton acorralado en la ultima fila del tablero    
            elif ((gato1==mouse-9 or gato2==mouse-9 or gato3==mouse-9 or gato4==mouse-9) and (gato1==mouse-7 or gato2==mouse-7 or gato3==mouse-7 or gato4==mouse-7) and (mouse>=56 and mouse<=63)):
                context_dict["winner"] = "gato"
                context_dict['final_partida'] = True
                context_dict['gana_gato'] = True
                return render(request, 'server/winner.html', context_dict)
        

            else:
                return render(request, 'server/winner.html', context_dict)

def show (request):
    games = Game.objects.order_by("-id")
     
    if games.exists():
        game = games[0]
        request.session["gameID"] = game.id
        return render(request, 'server/show.html', {})
    else:
        return

def show_board(request):
    board = list(range(0, 64))
    # Inicializa el tablero
    for i in range(64):
        board[i]=0
    g = Game.objects.filter(id=request.session["gameID"])
    g = g[0]
    board[g.cat1]=1
    board[g.cat2]=1
    board[g.cat3]=1
    board[g.cat4]=1
    board[g.mouse]=-1
    return render(request, 'server/show_ajax.html', {'board': board})
