# Uncomment if you want to run tests in transaction mode with a final rollback
#from django.test import TestCase
#uncomment this if you want to keep data after running tests
from unittest import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client
from server.models import Game, Move, Counter

#python ./manage.py test rango.tests.UserAuthenticationTests --keepdb
#class UserAuthenticationTests(TestCase):

usernameCat = 'gatoUser'
passwdCat = 'gatoPasswd'
usernameMouse = 'ratonUser'
passwdMouse = 'ratonPasswd'
DEBUG = False

class ServerTests(TestCase):
    def setUp(self):
        self.clientCat   = Client()
        self.clientMouse = Client()

    def creatUser(self, userName, userPassword):
        try:
            user = User.objects.get(username=userName)
        except User.DoesNotExist:
            user = User(username=userName, password=userPassword)
            user.set_password(user.password)
            user.save()
        return user.id

    def login(self, userName, userPassword, client):
        response = client.get(reverse('login_user'))
        self.assertIn(b'Login', response.content)
        loginDict={}
        loginDict["username"]=userName
        loginDict["password"]=userPassword
        response = client.post(reverse('login_user'), loginDict, follow=True)
        return response


    def deleteUser(self, userName):
        try:
            userKK = User.objects.get(username=userName)
            userKK.delete()
        except User.DoesNotExist:
            pass

    def logout(self, client):
        try:
            response = client.get(reverse('logout_user'), follow=True)
            self.assertEqual(response.status_code, 200)
            return response
        except:
            pass



    def test_counter_page(self):
        """call counter'"""
        Counter.objects.all().delete()
        counter = Counter()
        counter.counter=1
        counter.save()

        response = self.clientCat.get(reverse('counter'), follow=True)
        self.assertIn(b'Counter session: <strong>1</strong>', response.content)

        response = self.clientCat.get(reverse('counter'), follow=True)
        self.assertIn(b'Counter session: <strong>2</strong>', response.content)
        self.assertIn(b'Counter global: <strong>2</strong>', response.content)

        response = self.clientMouse.get(reverse('counter'), follow=True)
        self.assertIn(b'Counter session: <strong>1</strong>', response.content)
        self.assertIn(b'Counter global: <strong>3</strong>', response.content)

        response = self.clientCat.get(reverse('counter'), follow=True)
        self.assertIn(b'Counter session: <strong>3</strong>', response.content)
        self.assertIn(b'Counter global: <strong>4</strong>', response.content)
        if DEBUG: print response.content

    def test_register_page(self):
        """  test user creation functions using web form"""
        #delete user if it exists
        self.deleteUser(usernameCat)

        loginDict={}
        loginDict["username"]=usernameCat
        loginDict["password"]=passwdCat

        response = self.clientCat.post(reverse('register_user'), loginDict, follow=True)#follow redirection
        self.assertEqual(response.status_code, 200)#redirection
        userKK = User.objects.get(username=usernameCat)
        self.assertEqual(usernameCat,userKK.username)

    def test_login_page(self):
        """check that default page with login return 'Rango says username'
           and without login 'Rango says ... hello world'"""
        #check if user exists. if not create one
        self.creatUser( usernameCat, passwdCat)
        #logout (just in case)
        response = self.logout(self.clientCat)
        #login
        self.login(usernameCat,passwdCat, self.clientCat)
        response = self.clientCat.get(reverse('login_user'))#follow redirection
        self.assertIn(b'Login', response.content)
        loginDict={}
        loginDict["username"]=usernameCat
        loginDict["password"]=passwdCat
        response = self.clientCat.post(reverse('login_user'), loginDict, follow=True)#follow redirection
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome %s'%usernameCat, response.content)
        self.assertNotIn(b'Login %s', response.content)
        if DEBUG: print response.content


    def test_logout_page(self):
        #make sure cat user exists
        self.creatUser(usernameCat,passwdCat)
        #try to login_out   before logging in
        self.logout(self.clientCat)
        #logout with no login
        response = self.logout(self.clientCat)
        self.assertIn(b'You are not logged', response.content)
        #login
        response = self.login(usernameCat,passwdCat,self.clientCat)
        response = self.logout(self.clientCat)
        self.assertIn(b'Dear %s you have been logged out'%usernameCat,response.content)
        if DEBUG: print response.content

    def test_game_page(self):
        #make sure cat user exists
        self.creatUser(usernameCat, passwdCat)
        #try to login_out   before logging in
        response = self.logout(self.clientCat)
        self.assertIn(b'You are not logged', response.content)
        #login
        response = self.login(usernameCat, passwdCat, self.clientCat)
        self.assertIn(b'Login', response.content)
        response = self.clientCat.get(reverse('create_game'))#follow redirection
        self.assertIn(b'you have create a game with id',response.content)
        self.assertIn(b'catTurn = True',response.content)
        if DEBUG: print response.content

    def test_join_page(self):
        #make sure cat user exists
        self.creatUser(usernameCat, passwdCat)
        #make sure mouse user exists
        self.creatUser(usernameMouse, passwdMouse)
        #delete all orphan pages
        response = self.clientCat.get(reverse('clean_orphan_games'))
        #login
        #try to login_out   before logging in
        self.logout(self.clientCat)
        self.logout(self.clientMouse)
        #login
        response = self.login(usernameCat, passwdCat,self.clientCat)
        response = self.login(usernameMouse, passwdMouse,self.clientMouse)
        #create game
        response = self.clientCat.get(reverse('create_game'))#follow redirection
        self.assertEqual(response.status_code, 200)
        #very likely the last game is the one we just crated
        lastGame = Game.objects.all().order_by("-id")[0]
        self.assertEqual(response.status_code, 200)

        response = self.clientMouse.get(reverse('join_game'))
        self.assertIn(b'You have joined the game with id: %d'%lastGame.id,response.content)
        if DEBUG: print response.content

    def test_move_page(self):
        #make sure cat user exists
        userCatId   = self.creatUser(usernameCat, passwdCat)
        #make sure mouse user exists
        userMouseID = self.creatUser(usernameMouse, passwdMouse)
        #delete all orphan pages
        response = self.clientCat.get(reverse('clean_orphan_games'))
        #login
        response = self.login(usernameCat, passwdCat,self.clientCat)
        response = self.login(usernameMouse, passwdMouse,self.clientMouse)
        #create game
        response = self.clientCat.get(reverse('create_game'))#follow redirection
        self.assertEqual(response.status_code, 200)
        #join game
        response = self.clientMouse.get(reverse('join_game'))
        #move 2 ->11, valid move
        moveDict={}
        moveDict['origin']=2
        moveDict['target']=11
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'catUser = %s (%d)'%(usernameCat, userCatId),response.content)#catUser   = gatoUser (1)
        self.assertIn(b'mouseUser = %s (%d)'%(usernameMouse, userMouseID),response.content)#catUser   = gatoUser (1)
        #very likely the last game is the one we just crated
        lastGame = Game.objects.all().order_by("-id")[0]
        self.assertIn(b'gameId = %d'%lastGame.id,response.content)
        #very likely the last move is the one we just crated
        lastMove = Move.objects.all().order_by("-id")[0]
        self.assertIn(b'moveId (origin/target) = %d (%d/%d)'%(lastMove.id,lastMove.origin, lastMove.target),response.content)#moveId (origin/target)   = 9 (2/11)
        # repeat move this time it will be invalid
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertIn(b'Cannot create a move', response.content)
        #cat tries to move again
        moveDict['origin']=4
        moveDict['target']=13
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cannot create a move', response.content)
        #mouse moves
        moveDict['origin']=59#not needed
        moveDict['target']=52
        response = self.clientMouse.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'mouseUser = %s (%d)'%(usernameMouse, userMouseID),response.content)#catUser   = gatoUser (1)
        #cat move to wrong place
        moveDict['origin']=0#not needed
        moveDict['target']=15
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cannot create a move',response.content)#catUser   = gatoUser (1)
        #cat move to wrong place
        moveDict['origin']=0#not needed
        moveDict['target']=9
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'catUser = %s (%d)'%(usernameCat, userCatId),response.content)#catUser   = gatoUser (1)
        #mouse moves back
        moveDict['target']=52#not needed
        moveDict['target']=59
        response = self.clientMouse.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'mouseUser = %s (%d)'%(usernameMouse, userMouseID),response.content)#catUser   = gatoUser (1)
        #cat move to  place with another cat
        moveDict['origin']=4
        moveDict['target']=11
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b' cannot be a cat in the target',response.content)#catUser   = gatoUser (1)
        #cat moves back
        moveDict['origin']=11
        moveDict['target']=2
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b' you must move to a contiguous diagonal place',response.content)#catUser   = gatoUser (1)

    def test_status_turn(self):
        #make sure cat user exists
        userCatId   = self.creatUser(usernameCat, passwdCat)
        #make sure mouse user exists
        userMouseID = self.creatUser(usernameMouse, passwdMouse)
        #delete all orphan pages
        response = self.clientCat.get(reverse('clean_orphan_games'))
        #login
        response = self.login(usernameCat, passwdCat,self.clientCat)
        response = self.login(usernameMouse, passwdMouse,self.clientMouse)
        #create game
        response = self.clientCat.get(reverse('create_game'))#follow redirection
        self.assertEqual(response.status_code, 200)
        #join game
        response = self.clientMouse.get(reverse('join_game'))
        # cat turn
        response = self.clientCat.get(reverse('status_turn'))
        self.assertIn(b'It is your turn : True',response.content)#catUser   = gatoUser (1)
        response = self.clientMouse.get(reverse('status_turn'))
        self.assertIn(b'It is your turn : False',response.content)#catUser   = gatoUser (1)
        #move 2 ->11, valid move
        moveDict={}
        moveDict['origin']=2
        moveDict['target']=11
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        response = self.clientCat.get(reverse('status_turn'))
        self.assertIn(b'It is your turn : False',response.content)#catUser   = gatoUser (1)
        response = self.clientMouse.get(reverse('status_turn'))
        self.assertIn(b'It is your turn : True',response.content)#catUser   = gatoUser (1)
        self.assertNotIn(b'It is your turn : False',response.content)#catUser   = gatoUser (1)

    def test_status_board(self):
        #make sure cat user exists
        userCatId   = self.creatUser(usernameCat, passwdCat)
        #make sure mouse user exists
        userMouseID = self.creatUser(usernameMouse, passwdMouse)
        #delete all orphan pages
        response = self.clientCat.get(reverse('clean_orphan_games'))
        #login
        response = self.login(usernameCat, passwdCat,self.clientCat)
        response = self.login(usernameMouse, passwdMouse,self.clientMouse)
        #create game
        response = self.clientCat.get(reverse('create_game'))#follow redirection
        self.assertEqual(response.status_code, 200)
        #join game
        response = self.clientMouse.get(reverse('join_game'))
        # cat turn
        response = self.clientCat.get(reverse('status_board'))
        self.assertIn(b"""\n\n    \n    \n        <tr>\n            <td id=id_0 style=\'width: 20px\'>""",response.content)#catUser   = gatoUser (1)
        #cat move
        moveDict={}
        moveDict['origin']=4
        moveDict['target']=13
        response = self.clientCat.post(reverse('move'), moveDict)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"""\n\n    \n    \n        <tr>\n            <td id=id_0 >""",response.content)#catUser   = gatoUser (1)
