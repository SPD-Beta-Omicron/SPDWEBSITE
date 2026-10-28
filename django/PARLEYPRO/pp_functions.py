from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import *
from AUTHENTICATE.models import Brother_Profile


def count_all_current_votes(all_votes):
    nay_votes = all_votes.filter(user_vote_choice='Nay').count()
    aye_votes = all_votes.filter(user_vote_choice='Aye').count()
    return aye_votes, nay_votes 

def handling_end_vote_request(request, all_votes):
    '''
    When a user ends a vote, first they're check to be EXEC, 
    if they are exec then the current poll's information gets ready to be saved,
    then the poll is ended
    
    '''
    brother_profile = Brother_Profile.objects.get(user=request.user)
    current_poll = Vote_Poll.objects.filter(Vote_Poll_End__isnull=True).order_by('-Vote_Poll_Start').first()
    user_roles = list(brother_profile.roles.values_list('name', flat=True))
        
    if 'EXEC' not in user_roles:
        messages.error(request, "You need to be an EXEC member to end votes.")
        
    if current_poll:
        # Get final vote counts
        aye_votes, nay_votes = count_all_current_votes(all_votes)
        
        # Update the poll with final counts
        current_poll.Vote_Poll_Count_Yes = aye_votes
        current_poll.Vote_Poll_Count_No = nay_votes
        current_poll.Vote_Poll_End = timezone.now()
        current_poll.save()
        
        # Reset all votes to 'No Vote'
        all_votes.all().update(user_vote_choice='No Vote')
        
   
    
def Vote_Yes_No_or_StartANDEndVote(request, all_votes):
    '''
    This code handles the user flow for the public poll page
    End vote can only be accessed by an exec positon AND does more 
    actions so that is a called function.

    '''
    if 'start_vote' in request.POST:
        redirect("start_vote")

    elif 'end_vote' in request.POST:
    # Get the current active poll
        handling_end_vote_request(request, all_votes)
     

    else:
        vote, created = Brother_votes.objects.get_or_create(
        user=request.user,
        defaults={'user_vote_choice': 'No Vote'}  # Default value for new records
    )
        vote = Brother_votes.objects.get(user=request.user)
        if 'nay' in request.POST:
            vote.user_vote_choice = 'Nay'
            vote.save()
        if 'aye' in request.POST:
            vote.user_vote_choice = 'Aye'
            vote.save()
    return
            