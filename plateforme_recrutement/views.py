from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Recruteur, Offre, Candidat, UserProfil
from .forms import InscriptionForm, ConnexionForm, UserProfileForm, RecruteurProfileForm, CandidatProfileForm, OffreForm
import unicodedata


def normalize_text(text):
    """Normalize text by removing accents for case-insensitive, accent-insensitive comparison."""
    if not text:
        return ''
    # Decompose accented characters (é -> e + combining accent)
    nfkd_form = unicodedata.normalize('NFKD', text)
    # Filter out combining characters (accents)
    return ''.join(char for char in nfkd_form if not unicodedata.combining(char)).lower()

def inscription(request):
    form = InscriptionForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data

        user = User.objects.create_user(
            username   = data['username'],
            password   = data['password'],
            email      = data['email'],
            first_name = data['first_name'],
            last_name  = data['last_name'],
        )

        role = data['role']
        UserProfil.objects.create(user=user, role=role)

        if role == 'recruteur':
            Recruteur.objects.create(
                user       = user,
                entreprise = data['entreprise'],
                telephone  = data['telephone'],
                photo      = data.get('photo'),
            )
            login(request, user)
            return redirect('profil_recruteur')

        else:  # candidat
            Candidat.objects.create(
                user           = user,
                date_naissance = data.get('date_naissance'),
                telephone      = data['telephone'],
                ville          = data.get('ville'),
                pays           = data.get('pays'),
                photo          = data.get('photo'),
            )
            login(request, user)
            return redirect('profil_candidat')

    return render(request, 'plateforme/inscription.html', {'form': form})
 
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
            role = form.cleaned_data['role']
            login(request, user)

            if role == 'recruteur':
                return redirect('profil_recruteur')
            else:
                return redirect('profil_candidat')
        else:
            erreur = "Identifiants incorrects."

    return render(request, 'plateforme/connexion.html', {'form': form, 'erreur': erreur})

def deconnexion(request):
    logout(request)
    return redirect('connexion')


@login_required
def profil_recruteur(request):
    recruteur = get_object_or_404(Recruteur, user=request.user)

    if request.method == 'POST':

        if 'update_profile' in request.POST:
            user_form = UserProfileForm(request.POST, instance=request.user)
            recruteur_form = RecruteurProfileForm(
                request.POST,
                request.FILES,
                instance=recruteur
            )

            if user_form.is_valid() and recruteur_form.is_valid():
                user = user_form.save(commit=False)

                new_password = user_form.cleaned_data.get('new_password')

                if new_password:
                    user.set_password(new_password)

                user.save()
                recruteur_form.save()

                if new_password:
                    update_session_auth_hash(request, user)

                return redirect('profil_recruteur')

        elif 'delete_account' in request.POST:
            request.user.delete()
            return redirect('connexion')

    else:
        user_form = UserProfileForm(instance=request.user)
        recruteur_form = RecruteurProfileForm(instance=recruteur)

    return render(request, 'plateforme/profil_recruteur.html', {
        'user_form': user_form,
        'recruteur_form': recruteur_form,
        'recruteur': recruteur,
    })


@login_required
def mes_offres(request):
    recruteur = get_object_or_404(Recruteur, user=request.user)
    q = request.GET.get('q', '').strip()

    offres = Offre.objects.filter(recruteur=recruteur).order_by('-date_publication', '-id')
    
    if q:
        # Normalize the search query for accent-insensitive matching
        normalized_q = normalize_text(q)
        # Filter in Python to handle accented characters correctly
        offres = [offre for offre in offres if normalized_q in normalize_text(offre.titre)]

    return render(request, 'plateforme/mes_offres.html', {
        'recruteur': recruteur,
        'offres': offres,
        'q': q,
        'total_offres': Offre.objects.filter(recruteur=recruteur).count(),
        'offres_filtrees': len(offres) if q else Offre.objects.filter(recruteur=recruteur).count(),
    })


@login_required
def creer_offre(request):
    recruteur = get_object_or_404(Recruteur, user=request.user)
    form = OffreForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        offre = form.save(commit=False)
        offre.recruteur = recruteur
        offre.save()
        return redirect('mes_offres')

    return render(request, 'plateforme/offre_form.html', {
        'recruteur': recruteur,
        'form': form,
        'offre': None,
    })


@login_required
def modifier_offre(request, offre_id):
    recruteur = get_object_or_404(Recruteur, user=request.user)
    offre = get_object_or_404(Offre, id=offre_id, recruteur=recruteur)
    form = OffreForm(request.POST or None, instance=offre)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('mes_offres')

    return render(request, 'plateforme/offre_form.html', {
        'recruteur': recruteur,
        'form': form,
        'offre': offre,
    })


@login_required
def supprimer_offre(request, offre_id):
    recruteur = get_object_or_404(Recruteur, user=request.user)
    offre = get_object_or_404(Offre, id=offre_id, recruteur=recruteur)

    if request.method == 'POST':
        offre.delete()
        return redirect('mes_offres')

    return redirect('mes_offres')


@login_required
def profil_candidat(request):
    candidat = get_object_or_404(Candidat, user=request.user)

    if request.method == 'POST':

        if 'update_profile' in request.POST:
            user_form = UserProfileForm(request.POST, instance=request.user)
            candidat_form = CandidatProfileForm(
                request.POST,
                request.FILES,
                instance=candidat
            )

            if user_form.is_valid() and candidat_form.is_valid():
                user = user_form.save(commit=False)

                new_password = user_form.cleaned_data.get('new_password')

                if new_password:
                    user.set_password(new_password)

                user.save()
                candidat_form.save()

                if new_password:
                    update_session_auth_hash(request, user)

                return redirect('profil_candidat')

        elif 'delete_account' in request.POST:
            request.user.delete()
            return redirect('connexion')

    else:
        user_form = UserProfileForm(instance=request.user)
        candidat_form = CandidatProfileForm(instance=candidat)

    return render(request, 'plateforme/profil_candidat.html', {
        'user_form': user_form,
        'candidat_form': candidat_form,
        'candidat': candidat,
    })
@login_required
def offres_dispo(request):
    candidat = get_object_or_404(Candidat, user=request.user)

    q = request.GET.get('q', '').strip()

    offres = Offre.objects.select_related('recruteur', 'recruteur__user').all().order_by('-date_publication', '-id')

    if q:
        offres = offres.filter(
            Q(titre__icontains=q) |
            Q(description__icontains=q) |
            Q(recruteur__entreprise__icontains=q)
        )

    return render(request, 'plateforme/offres_dispo.html', {
        'candidat': candidat,
        'offres': offres,
        'q': q,
    })