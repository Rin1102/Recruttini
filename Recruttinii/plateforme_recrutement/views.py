from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from .models import Recruteur, Offre, Candidat, UserProfil, Candidature
from .forms import (
    InscriptionForm,
    ConnexionForm,
    UserProfileForm,
    RecruteurProfileForm,
    CandidatProfileForm,
    OffreForm,
    CandidatureForm,
    EntretienForm,
)
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
    candidatures_en_attente_offres_ids = set(
        candidat.candidatures.filter(statut='en_attente').values_list('offre_id', flat=True)
    )

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
        'candidatures_en_attente_offres_ids': candidatures_en_attente_offres_ids,
    })


@login_required
def postuler_offre(request, offre_id):
    candidat = get_object_or_404(Candidat, user=request.user)
    offre = get_object_or_404(Offre.objects.select_related('recruteur'), id=offre_id)

    candidature_existante = Candidature.objects.filter(
        offre=offre,
        candidat=candidat,
        statut='en_attente',
    ).first()
    if candidature_existante:
        messages.info(request, "Vous avez déjà une candidature en attente pour cette offre.")
        return redirect('mes_candidatures')

    initial_data = {
        'nom': request.user.last_name,
        'prenom': request.user.first_name,
        'telephone': candidat.telephone,
        'ville': candidat.ville,
        'email': request.user.email,
    }

    form = CandidatureForm(request.POST or None, request.FILES or None, initial=initial_data)

    if request.method == 'POST' and form.is_valid():
        candidature = form.save(commit=False)
        candidature.offre = offre
        candidature.candidat = candidat
        candidature.save()
        messages.success(request, "Votre candidature a été envoyée avec succès.")
        return redirect('mes_candidatures')

    return render(request, 'plateforme/candidature_form.html', {
        'candidat': candidat,
        'offre': offre,
        'form': form,
    })


@login_required
def mes_candidatures(request):
    candidat = get_object_or_404(Candidat, user=request.user)
    candidatures = (
        Candidature.objects
        .select_related('offre', 'offre__recruteur')
        .filter(candidat=candidat)
        .order_by('-date_soumission')
    )

    return render(request, 'plateforme/mes_candidatures.html', {
        'candidat': candidat,
        'candidatures': candidatures,
    })


@login_required
def suivi_candidatures(request):
    recruteur = get_object_or_404(Recruteur, user=request.user)
    candidatures = (
        Candidature.objects
        .select_related('offre', 'candidat', 'candidat__user')
        .filter(offre__recruteur=recruteur, statut='en_attente')
        .order_by('-date_soumission')
    )

    return render(request, 'plateforme/suivi_candidatures.html', {
        'recruteur': recruteur,
        'candidatures': candidatures,
    })


@login_required
def changer_statut_candidature(request, candidature_id):
    recruteur = get_object_or_404(Recruteur, user=request.user)
    candidature = get_object_or_404(
        Candidature,
        id=candidature_id,
        offre__recruteur=recruteur,
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'rejeter':
            candidature.statut = 'rejetee'
            candidature.save(update_fields=['statut'])
            messages.success(request, "La candidature a été rejetée.")
            return redirect('suivi_candidatures')

        form = EntretienForm(request.POST, instance=candidature)
        if form.is_valid():
            candidature = form.save(commit=False)
            candidature.statut = 'acceptee'
            candidature.save()
            messages.success(request, "Candidature acceptée et entretien planifié.")
            return redirect('suivi_candidatures')

        return render(request, 'plateforme/entretien_form.html', {
            'recruteur': recruteur,
            'candidature': candidature,
            'form': form,
        })

    if candidature.statut != 'en_attente':
        messages.info(request, "Cette candidature n'est plus en attente.")
        return redirect('suivi_candidatures')

    form = EntretienForm(instance=candidature)
    return render(request, 'plateforme/entretien_form.html', {
        'recruteur': recruteur,
        'candidature': candidature,
        'form': form,
    })


@login_required
def entretiens_recruteur(request):
    recruteur = get_object_or_404(Recruteur, user=request.user)
    today = timezone.localdate()
    entretiens = (
        Candidature.objects
        .select_related('offre', 'candidat', 'candidat__user')
        .filter(
            offre__recruteur=recruteur,
            statut='acceptee',
            entretien_date__gte=today,
            entretien_heure__isnull=False,
            entretien_type__in=['hybrid', 'onsite'],
            entretien_lieu__gt='',
            entretien_message__gt='',
        )
        .order_by('entretien_date', 'entretien_heure')
    )

    return render(request, 'plateforme/entretiens_recruteur.html', {
        'recruteur': recruteur,
        'entretiens': entretiens,
    })


@login_required
def mes_entretiens_candidat(request):
    candidat = get_object_or_404(Candidat, user=request.user)
    today = timezone.localdate()
    entretiens = (
        Candidature.objects
        .select_related('offre', 'offre__recruteur')
        .filter(
            candidat=candidat,
            statut='acceptee',
            entretien_date__gte=today,
            entretien_heure__isnull=False,
            entretien_type__in=['hybrid', 'onsite'],
            entretien_lieu__gt='',
            entretien_message__gt='',
        )
        .order_by('entretien_date', 'entretien_heure')
    )

    return render(request, 'plateforme/mes_entretiens_candidat.html', {
        'candidat': candidat,
        'entretiens': entretiens,
    })