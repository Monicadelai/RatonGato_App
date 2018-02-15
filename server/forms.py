from django import forms

from django.contrib.auth.models import User

from server.models import Move

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')
        help_texts = {
            'username': None,
        }
    
class MoveForm(forms.ModelForm):

    class Meta:
        model = Move
        fields = ('origin', 'target')
