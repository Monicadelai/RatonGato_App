# lucnh this script and as mouse first clean orphan games and then
# join the game
import os,django
os.environ['DJANGO_SETTINGS_MODULE'] =  'RatonGato.settings'
django.setup()
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client
from server.models import Game, Move, Counter
import time
import re, math
import random, json

#python ./manage.py test rango.tests.UserAuthenticationTests --keepdb
#class UserAuthenticationTests(TestCase):

usernameCat = 'gatoUser'
passwdCat = 'gatoPasswd'
usernameMouse = 'ratonUser'
passwdMouse = 'ratonPasswd'
DEBUG = False

class CatPlayer():
    def __init__(self):
        self.clientCat = Client()
        self.cats = [0, 2, 4, 6]
        self.game=None
        currenTime = time.time()
        RandomSeed = int(currenTime) + os.getpid()
        random.seed(RandomSeed)

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
        print ("wait loop begin")
        while True:
            response = self.clientCat.get(reverse('status_turn2'))
	    print (response.content)
            if response.content.find(key) != -1:
                break
            time.sleep(seconds)
            print ".",
        print ("wait loop end")
        return 0

    def parse_mouse(self):
        """http://pythex.org/"""
        response = self.clientCat.get(reverse('status_board'))
        print "response.content", response.content
        searchString='<td id=id_(\d+) onclick="getID\(this\);" >\s+&#9920;'
                       #<td id=id_0 onclick="getID(this);" >\n              &#9922;
        finds = re.findall(searchString,response.content)

        return finds[0]

    def validRandomMove(self,mousePosition):
        counter=0
        validMoves=[+7,+9]
        target = -1
        catIndex = -1
        origin = -1
        moveDict={}

        while True:
            counter += 1
            if counter > 1000:
                print "I cannot move. You won."
                exit(0)
            i = random.randrange(0,2)
            catIndex = random.randrange(0,4)

            origin = self.cats[catIndex]
            target = origin + validMoves[i]
            print("origin target cats", origin, target, self.cats)
            #cannot be a cat
            if mousePosition == target:
                 print("continue mouseposition", mousePosition,target )
                 continue
            #canot be a cat in target
            continueit=False
            for cat in self.cats:
                if cat == target:
                    print("continue cats")
                    continueit = True
            if continueit:
                continue
            #can not move two rows o no row
            if not ( 1 + (origin//8)) ==(target//8) :
                 print("continue no two rows")
                 continue
            # if target in the right range break
            if target < 0 or target > 63:
                print("continue target self.cats, target ",self.cats, target)
                continue

            moveDict['origin']=origin
            moveDict['target']=target
            response = CatPlayer.clientCat.post(reverse('move'), moveDict)
            key ="Error"
            if response.content.find(key) != -1:
                continue
            else:
                break
            #return render(request, 'server/move.html', moveDict)
            #CHANGE THIS
            #return HttpResponse(json.dumps({'error':error, 'moveDone':moveDone}),
            #        content_type="application/json"
            #    )

            #responseDict = json.loads(response.content)
        return origin,target
        #try to move
    def set_catPosition(self,origin, position):
        for cat in range(0,4):
            if self.cats[cat] == origin:
                self.cats[cat] = target
                break
        print("self.cats",self.cats)

CatPlayer = CatPlayer()
#make sure mouse user exists
userCatID = CatPlayer.creatUser(usernameCat, passwdCat)
#login
response = CatPlayer.login(usernameCat, passwdCat,CatPlayer.clientCat)
#create game
response = CatPlayer.clientCat.get(reverse('create_game'))
#get last game id
game = Game.objects.latest("id")
print "cat creates game", game
#check if mouse has joined
print("waiting untill mouse joins")
while True:
     time.sleep(1)
     gameOK = Game.objects.filter(mouseUser__isnull=True).order_by("-id")
     if gameOK.exists():
         game2 = gameOK[0]
         if game.id == game2.id:
             print ".",
             continue
     else:
         break
print("game id=%d"%game.id)
moveDict={}
while True:
     # loop waiting for myTurn=True
     CatPlayer.wait_loop(1)# time in second between retrial

     #moveDict['origin']=0
     #moveDict['target']=9
     #response = CatPlayer.clientCat.post(reverse('move'), moveDict)

     # parse mouse position
     mousePosition = CatPlayer.parse_mouse()
     print('mousePosition', mousePosition)
     #create random cat move
     origin, target = CatPlayer.validRandomMove(mousePosition)
     #move
     CatPlayer.set_catPosition(origin, target)

