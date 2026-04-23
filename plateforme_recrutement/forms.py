from django import forms
from django.contrib.auth.models import User
from .models import Recruteur,Offre

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


class UserProfileForm(forms.ModelForm):
    new_password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        required=False
    )
    confirm_password = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password or confirm_password:
            if not new_password or not confirm_password:
                raise forms.ValidationError("Veuillez remplir les deux champs de mot de passe.")
            if new_password != confirm_password:
                raise forms.ValidationError("Les mots de passe ne correspondent pas.")
            if len(new_password) < 8:
                raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

        return cleaned_data


class RecruteurProfileForm(forms.ModelForm):
    class Meta:
        model = Recruteur
        fields = ['entreprise', 'telephone', 'photo']