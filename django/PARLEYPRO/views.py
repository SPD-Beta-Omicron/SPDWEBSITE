from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *
from .pp_functions import *
from AUTHENTICATE.permissions import requires_role
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import VotePollForm
from django.http import JsonResponse

@requires_role('ACTIVE')
@login_required
def poll_index(request):
    #print(request.POST)
   
    all_votes = Brother_votes.objects
    # Get the most recent active poll (where Vote_Poll_End is null)
    current_poll = Vote_Poll.objects.filter(Vote_Poll_End__isnull=True).order_by('-Vote_Poll_Start').first()
    
    if request.method == 'POST':
        Vote_Yes_No_or_StartANDEndVote(request, all_votes)

    (aye_votes, nay_votes) = count_all_current_votes(all_votes)

    context = {
        'nay_votes': nay_votes,
        'aye_votes': aye_votes,
        'current_poll': current_poll,
    }
    return render(request, 'PARLEYPRO/poll_index.html', context)
@login_required
@requires_role('EXEC','ACTIVE')
def start_vote(request):
    if request.method == 'POST':
        form = VotePollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.created_by = request.user
            poll.Vote_Poll_Start = timezone.now()  # Set the start time
            poll.save()
            return redirect('poll')  # Make sure this matches your URL name
    else:
        form = VotePollForm()
    
    context = {'form': form}
    return render(request, 'PARLEYPRO/create_poll.html', context)
@requires_role('ACTIVE')
@login_required
def past_polls(request):
    past_polls = Vote_Poll.objects.filter(
        Vote_Poll_End__isnull=False
    ).order_by('-Vote_Poll_End')
    
    return render(request, 'PARLEYPRO/past_polls.html', {'past_polls': past_polls})


@login_required # Used for Live Update
def poll_results(request):
    aye_votes = Brother_votes.objects.filter(user_vote_choice='Aye').count()
    nay_votes = Brother_votes.objects.filter(user_vote_choice='Nay').count()
    return JsonResponse({
        'aye_votes': aye_votes,
        'nay_votes': nay_votes
    })