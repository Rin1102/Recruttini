from django.db import models
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
    
class Candidat(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    date_naissance=models.DateField(null=True,blank=True)
    telephone=models.CharField(max_length=20,blank=True)
    ville=models.CharField(max_length=100,blank=True)
    pays=models.CharField(max_length=100,blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} "
    

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