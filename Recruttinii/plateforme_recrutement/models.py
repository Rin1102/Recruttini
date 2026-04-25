from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

ROLE_CHOICES=[
  ('recruteur','Recrteur'),
  ('candidat','Candidat'),
]

class UserProfil(models.Model):
    user =models.OneToOneField(User,on_delete=models.CASCADE)
    role=models.CharField(max_length=20,choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username}- {self.role}"


class Recruteur(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    entreprise=models.CharField(max_length=150)
    telephone=models.CharField(max_length=20,blank=True)
    photo=models.ImageField(upload_to='recruteurs/',blank=True,null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}-{self.entreprise}"

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()
    
class Candidat(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    date_naissance=models.DateField(null=True,blank=True)
    telephone=models.CharField(max_length=20,blank=True)
    ville=models.CharField(max_length=100,blank=True)
    pays=models.CharField(max_length=100,blank=True)
    photo=models.ImageField(upload_to='candidats/',blank=True,null=True)  # ← AJOUTER
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} "

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()
    

class Offre(models.Model):
    TYPE_CONTRAT_CHOICES = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('Stage', 'Stage'),
        ('Alternance', 'Alternance'),
    ]

    recruteur=models.ForeignKey(Recruteur,on_delete=models.CASCADE)
    titre=models.CharField(max_length=200)
    description=models.TextField()
    lieu=models.CharField(max_length=150, default='', blank=True)
    type_contrat=models.CharField(max_length=20, choices=TYPE_CONTRAT_CHOICES, default='', blank=True)
    salaire=models.IntegerField(null=True, blank=True)
    competences=models.TextField(default='', blank=True)
    date_limite=models.DateField(null=True, blank=True)
    date_publication=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.titre


class Candidature(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('rejetee', 'Rejetée'),
    ]
    ENTRETIEN_TYPE_CHOICES = [
        ('hybrid', 'Hybride'),
        ('onsite', 'Sur site'),
    ]

    offre = models.ForeignKey(Offre, on_delete=models.CASCADE, related_name='candidatures')
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='candidatures')

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    ville = models.CharField(max_length=100)

    github_link = models.URLField(blank=True)
    cv = models.FileField(upload_to='candidatures/cv/')

    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    entretien_date = models.DateField(null=True, blank=True)
    entretien_heure = models.TimeField(null=True, blank=True)
    entretien_type = models.CharField(max_length=20, choices=ENTRETIEN_TYPE_CHOICES, blank=True, default='')
    entretien_lieu = models.CharField(max_length=255, blank=True, default='')
    entretien_message = models.TextField(blank=True, default='')
    date_soumission = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['offre', 'candidat'],
                condition=Q(statut='en_attente'),
                name='unique_pending_candidature_per_offre_candidat',
            )
        ]
        ordering = ['-date_soumission']

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.offre.titre}"