from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.auth.models import User

class Game(models.Model):
    catUser = models.ForeignKey(User, related_name='game_catUsers')
    mouseUser = models.ForeignKey(User, related_name='game_mouseUsers', null = True)
    cat1 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(63)])
    cat2 = models.IntegerField(default=2, validators=[MinValueValidator(0), MaxValueValidator(63)])
    cat3 = models.IntegerField(default=4, validators=[MinValueValidator(0), MaxValueValidator(63)])
    cat4 = models.IntegerField(default=6, validators=[MinValueValidator(0), MaxValueValidator(63)])
    mouse = models.IntegerField(default=59, validators=[MinValueValidator(0), MaxValueValidator(63)])
    catTurn = models.BooleanField(default=True)
    
    def __unicode__(self):
        return "gId=%d"%(self.id)

class Move(models.Model):
    origin = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(63)], null = False)
    target = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(63)], null = False)
    game = models.ForeignKey(Game, null = False)

    def __unicode__ (self):
        return "movId=%d (gId=%d)"%(self.id,self.game.id)

class Counter(models.Model):
    
    countGlobal = models.IntegerField(default=0)

    
	




