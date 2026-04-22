from django import forms
from .models import Recruteur,Offre
from django.contrib.auth.models import User

class InscriptionForm(forms.Form):
    username = forms.CharField(max_length=100, label="Nom d'utilisateur")
    first_name = forms.CharField(max_length=100, label="Prénom")
    last_name = forms.CharField(max_length=100, label="Nom")
    email = forms.EmailField(label="Email")
    entreprise = forms.CharField(max_length=150, label="Entreprise")
    telephone = forms.CharField(max_length=20, label="Téléphone", required=False)
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
class ConnexionForm(forms.Form):
    username = forms.CharField(max_length=100, label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['titre', 'description']
        # ⚠️ pas de champ recruteur, on le récupère via la session