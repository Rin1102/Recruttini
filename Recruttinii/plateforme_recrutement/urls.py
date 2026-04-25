from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/', views.profil_recruteur, name='profil_recruteur'),
    path('offres/', views.mes_offres, name='mes_offres'),
    path('offres/nouvelle/', views.creer_offre, name='creer_offre'),
    path('offres/<int:offre_id>/modifier/', views.modifier_offre, name='modifier_offre'),
    path('offres/<int:offre_id>/supprimer/', views.supprimer_offre, name='supprimer_offre'),
   path('profil-candidat/', views.profil_candidat, name='profil_candidat'),
   path('offres-disponibles/', views.offres_dispo, name='offres_dispo'),
    path('offres-disponibles/<int:offre_id>/postuler/', views.postuler_offre, name='postuler_offre'),
    path('mes-candidatures/', views.mes_candidatures, name='mes_candidatures'),
    path('suivi-candidatures/', views.suivi_candidatures, name='suivi_candidatures'),
    path('entretiens/', views.entretiens_recruteur, name='entretiens_recruteur'),
    path('suivi-candidatures/<int:candidature_id>/statut/', views.changer_statut_candidature, name='changer_statut_candidature'),
]