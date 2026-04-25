from django import forms
from django.contrib.auth.models import User
from .models import Recruteur, Offre,Candidat
import re

class InscriptionForm(forms.Form):

    ROLE_CHOICES = [
        ('candidat', 'Candidat'),
        ('recruteur', 'Recruteur'),
    ]

    role          = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select)
    username      = forms.CharField(max_length=100)
    first_name    = forms.CharField(max_length=100)
    last_name     = forms.CharField(max_length=100)
    email         = forms.EmailField()
    telephone     = forms.CharField(max_length=20)
    password      = forms.CharField(widget=forms.PasswordInput)
    photo         = forms.ImageField(required=False)

    # Recruteur
    entreprise    = forms.CharField(max_length=150, required=False)

    # Candidat
    date_naissance = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    ville          = forms.CharField(max_length=100, required=False)
    pays           = forms.CharField(max_length=100, required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 3:
            raise forms.ValidationError("Minimum 3 caractères.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):                                          # ✅ bien dans la classe
        email = self.cleaned_data['email'].strip().lower()
        domaine = email.split('@')[1]
        if '.' not in domaine:
            raise forms.ValidationError("Email invalide. Ex : exemple@domain.com")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_password(self):                                       # ✅ bien dans la classe
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError("Minimum 8 caractères.")
        if not any(c.isupper() for c in password):
            raise forms.ValidationError("Au moins une majuscule.")
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError("Au moins un chiffre.")
        return password

    def clean_telephone(self):
        tel = re.sub(r'[\s\-\.\(\)]', '', self.cleaned_data['telephone'])
        if not re.match(r'^\+?\d{8,15}$', tel):
            raise forms.ValidationError("Numéro invalide. Ex : 54212712")
        return tel

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Max 2 Mo.")
            if photo.content_type not in ['image/jpeg', 'image/png', 'image/webp']:
                raise forms.ValidationError("JPG, PNG ou WEBP uniquement.")
        return photo

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        if role == 'recruteur' and not cleaned_data.get('entreprise'):
            self.add_error('entreprise', "Champ obligatoire pour un recruteur.")
        return cleaned_data


class ConnexionForm(forms.Form):
    role = forms.ChoiceField(
        choices=[('candidat', 'Candidat'), ('recruteur', 'Recruteur')],
        widget=forms.Select(attrs={'class': 'form-input'}),
        label="Vous êtes ?"
    )
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        label="Nom d'utilisateur"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label="Mot de passe"
    )


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['titre', 'description', 'lieu', 'type_contrat', 'salaire', 'competences', 'date_limite']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'competences': forms.Textarea(attrs={'rows': 4}),
            'date_limite': forms.DateInput(attrs={'type': 'date'}),
            'salaire': forms.NumberInput(attrs={'type': 'number', 'min': '0'}),
        }
        labels = {
            'titre': 'Titre du poste',
            'description': 'Description',
            'lieu': 'Lieu',
            'type_contrat': 'Type de contrat',
            'salaire': 'Salaire',
            'competences': 'Compétences requises',
            'date_limite': 'Date limite de candidature',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titre'].widget.attrs.update({'placeholder': 'ex: Développeur Django'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Décrivez les missions...'})
        self.fields['lieu'].widget.attrs.update({'placeholder': 'ex: Tunis / Remote'})
        self.fields['salaire'].widget.attrs.update({'placeholder': 'ex: 50000'})
        self.fields['competences'].widget.attrs.update({'placeholder': 'Python, Django, REST, Git...'})
        self.fields['lieu'].required = True
        self.fields['type_contrat'].required = True
        self.fields['competences'].required = True

    def clean_salaire(self):
        salaire = self.cleaned_data.get('salaire')
        if salaire is not None and salaire < 0:
            raise forms.ValidationError("Le salaire ne peut pas être négatif.")
        return salaire


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


class CandidatProfileForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['date_naissance','telephone' ,'ville', 'pays' ,'photo']

