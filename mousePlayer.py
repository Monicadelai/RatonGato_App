# Using the browser create a game as cat and them
#launch this script
import os,django
os.environ['DJANGO_SETTINGS_MODULE'] =  'RatonGato.settings'
django.setup()
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client
from server.models import Game, Move, Counter
import time
import re, math
import random

#python ./manage.py test rango.tests.UserAuthenticationTests --keepdb
#class UserAuthenticationTests(TestCase):

usernameCat = 'gatoUser'
passwdCat = 'gatoPasswd'
usernameMouse = 'ratonUser'
passwdMouse = 'ratonPasswd'
DEBUG = False

class MousePlayer():
    def __init__(self):
        self.clientMouse = Client()
        self.mousePosition = 59
        currenTime = time.time()
        RandomSeed = int(currenTime) + os.getpid()

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
            return response
        except:
            pass

    def wait_loop(self, seconds):
        key = "It is your turn : True"
        while True:
            response = self.clientMouse.get(reverse('status_turn2'))
            if response.content.find(key) != -1:
                break
            time.sleep(seconds)
            print ".",
        return 0

    def parse_cats(self):
        """http://pythex.org/"""
        response = self.clientMouse.get(reverse('status_board'))
        searchString='<td id=id_(\d+) onclick="getID\(this\);" >\s+&#9922;'
                       #<td id=id_0 onclick="getID(this);" >\n              &#9922;
        finds = re.findall(searchString,response.content)
        print finds
        result = 0
        x = 1
        for find in finds:
            result += x << int(find)
        return result

    def validRandomMove(self,catPosition):
        counter = 0
        contador = 0
        validMoves=[+7,+9,-7,-9]
        x=1
        while True:
            print catPosition
            counter += 1
            if counter > 250:
                print "I cannot move. You won."
                exit(0)
            i = random.randrange(2,4)
            target = self.mousePosition + validMoves[i]
            if contador == 2:
                i = random.randrange(0,4)
                contador = 0
            target = self.mousePosition + validMoves[i]
            #cannot be a cat
            if target > 63:
                continue
            if target < 0:
                exit(0)
            if catPosition & (x << target):
                continue
            #can not move two rows
            origin = self.mousePosition
            if not ( (1+origin//8) == (target//8) or  (origin//8) == (1+target//8) ) :
                continue
            # if target in the right range break
            if target > 0 and target < 64:
                break
        return target
        #try to move
    def set_mousePosition(self,position):
        self.mousePosition=position

mousePlayer = MousePlayer()
#make sure mouse user exists
userMouseID = mousePlayer.creatUser(usernameMouse, passwdMouse)
#login
response = mousePlayer.login(usernameMouse, passwdMouse,mousePlayer.clientMouse)
#join game
response = mousePlayer.clientMouse.get(reverse('join_game'))
moveDict={}
while True:
     # loop waiting for myTurn=True
     mousePlayer.wait_loop(1)# time in second between retrial
     # parse cat position
     catPosition = mousePlayer.parse_cats()
     #create random mouse move
     target = mousePlayer.validRandomMove(catPosition)
     #put this in a while
     moveDict['origin']=59#not needed
     moveDict['target']=target
     response = mousePlayer.clientMouse.post(reverse('move'), moveDict)
     print("response",response)
     mousePlayer.set_mousePosition(target)

