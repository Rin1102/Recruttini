from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Recruteur
from .forms import InscriptionForm, ConnexionForm, UserProfileForm, RecruteurProfileForm


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
            return redirect('profil_recruteur')

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
            return redirect('profil_recruteur')
        else:
            erreur = "Identifiants incorrects."

    return render(request, 'plateforme/connexion.html', {'form': form, 'erreur': erreur})


def deconnexion(request):
    logout(request)
    return redirect('connexion')


@login_required
def profil_recruteur(request):
    recruteur = get_object_or_404(Recruteur, user=request.user)

    user_form = UserProfileForm(request.POST or None, instance=request.user)
    recruteur_form = RecruteurProfileForm(request.POST or None, request.FILES or None, instance=recruteur)

    if request.method == 'POST' and 'update_profile' in request.POST:
        if user_form.is_valid() and recruteur_form.is_valid():
            user_form.save()
            recruteur_form.save()
            return redirect('profil_recruteur')

    if request.method == 'POST' and 'delete_account' in request.POST:
        request.user.delete()
        return redirect('connexion')

    return render(request, 'plateforme/profil_recruteur.html', {
        'user_form': user_form,
        'recruteur_form': recruteur_form,
        'recruteur': recruteur,
    })