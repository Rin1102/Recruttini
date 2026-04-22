from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Recruteur
from .forms import InscriptionForm, ConnexionForm


def inscription(request):
    form = InscriptionForm(request.POST or None)
    erreur = None

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']

        if User.objects.filter(username=username).exists():
            erreur = "Ce nom d'utilisateur existe déjà."
        elif User.objects.filter(email=email).exists():
            erreur = "Cet email existe déjà."
        else:
            user = User.objects.create_user(
                username=username,
                password=form.cleaned_data['password'],
                email=email,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )

            Recruteur.objects.create(
                user=user,
                entreprise=form.cleaned_data['entreprise'],
                telephone=form.cleaned_data['telephone'],
            )

            login(request, user)
            return redirect('connexion')

    return render(request, 'plateforme/inscription.html', {'form': form, 'erreur': erreur})


def connexion(request):
    form = ConnexionForm(request.POST or None)
    erreur = None

    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )

        if user:
            login(request, user)
            return redirect('liste_offres')
        else:
            erreur = "Identifiants incorrects."

    return render(request, 'plateforme/connexion.html', {'form': form, 'erreur': erreur})


def deconnexion(request):
    logout(request)
    return redirect('connexion')