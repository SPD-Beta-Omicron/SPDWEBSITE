from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# class Vote_Tracker(models.Model):
#     Vote_name = models.CharField(max_length=200, null=True, blank=True)
#     No_votes = models.IntegerField(null=True, default=0)
#     Yes_votes = models.IntegerField(null=True, default=0)

#     def __str__(self):
#         return self.Vote_name
class Vote_Poll(models.Model):
    Vote_Poll_Name = models.CharField(max_length=200, null=True)
    Vote_Poll_Start = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    Vote_Poll_Count_Yes = models.IntegerField(blank=True, null=True, default=0)
    Vote_Poll_Count_No = models.IntegerField(blank=True, null=True, default=0)
    Vote_Poll_End = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_polls')


class Brother_votes(models.Model):
    vote_catergories =(('Aye','Aye'),('Nay','Nay'),('No Vote','No Vote'))
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    user_vote_choice= models.CharField(max_length=200, null=True, choices=vote_catergories)
