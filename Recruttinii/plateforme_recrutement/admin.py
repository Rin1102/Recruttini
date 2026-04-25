from django.contrib import admin
from .models import UserProfil, Recruteur, Candidat, Offre, Candidature


@admin.register(UserProfil)
class UserProfilAdmin(admin.ModelAdmin):
	list_display = ('user', 'role')
	search_fields = ('user__username', 'user__email', 'role')
	list_filter = ('role',)


@admin.register(Recruteur)
class RecruteurAdmin(admin.ModelAdmin):
	list_display = ('user', 'entreprise', 'telephone')
	search_fields = ('user__username', 'user__email', 'entreprise', 'telephone')


@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
	list_display = ('user', 'telephone', 'ville', 'pays', 'date_naissance')
	search_fields = ('user__username', 'user__email', 'telephone', 'ville', 'pays')
	list_filter = ('pays', 'ville')


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
	list_display = ('titre', 'recruteur', 'type_contrat', 'lieu', 'salaire', 'date_publication', 'date_limite')
	search_fields = ('titre', 'description', 'lieu', 'recruteur__user__username', 'recruteur__entreprise')
	list_filter = ('type_contrat', 'date_publication', 'date_limite')
	date_hierarchy = 'date_publication'


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
	list_display = (
		'offre', 'candidat', 'email', 'telephone', 'statut',
		'entretien_date', 'entretien_heure', 'entretien_type', 'entretien_lieu',
		'date_soumission'
	)
	search_fields = (
		'offre__titre', 'candidat__user__username', 'nom', 'prenom', 'email', 'telephone',
		'entretien_lieu', 'entretien_message'
	)
	list_filter = ('statut', 'entretien_type', 'entretien_date', 'date_soumission')
