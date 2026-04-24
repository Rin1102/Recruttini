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

   
]