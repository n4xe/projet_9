from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import Ticket, Review, UserFollows
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from itertools import chain
from operator import attrgetter

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.")
            return redirect('login')
        else:
            messages.error(request, "Une erreur est survenue lors de l'inscription. Veuillez réessayer.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form, 'errors': form.errors})


@login_required
def add_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('add_ticket')
    else:
        form = TicketForm()
    return render(request, 'ticket.html', {'form': form})

@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('add_ticket')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'ticket.html', {'form': form})

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    if request.method == 'POST':
        ticket.delete()
        return redirect('add_ticket')
    return render(request, 'ticket_confirm_delete.html', {'ticket': ticket})

@login_required
def add_review(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('ticket_detail', ticket_id=ticket.id)  # Redirection vers le détail du ticket
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form': form, 'ticket': ticket})


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            # Redirigez vers la page de détail de la critique ou une autre vue pertinente
            return redirect('review_detail', review_id=review.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'review_form.html', {'form': form, 'ticket': review.ticket})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == 'POST':
        review.delete()
        # Redirigez vers la liste des tickets ou une autre vue pertinente après la suppression
        return redirect('ticket_list')
    return render(request, 'review_confirm_delete.html', {'review': review})

@login_required
def user_follows(request):
    # Récupérer les abonnements de l'utilisateur
    follows = UserFollows.objects.filter(user=request.user)
    # Récupérer les utilisateurs qui suivent l'utilisateur courant
    followers = UserFollows.objects.filter(followed_user=request.user)
    return render(request, 'user_follows.html', {'follows': follows, 'followers': followers})

@login_required
def follow_user(request):
    if request.method == 'POST':
        form = UserFollowForm(request.POST)
        if form.is_valid():
            followed_user = User.objects.get(username=form.cleaned_data['username'])
            # Empêcher l'abonnement à soi-même
            if followed_user != request.user:
                UserFollows.objects.create(user=request.user, followed_user=followed_user)
            return redirect('user_follows')
    else:
        form = UserFollowForm()
    return render(request, 'follow_user.html', {'form': form})

@login_required
def unfollow_user(request, user_id):
    follow = get_object_or_404(UserFollows, user=request.user, followed_user_id=user_id)
    if request.method == 'POST':
        follow.delete()
        return redirect('user_follows')
    return render(request, 'unfollow_confirm.html', {'follow': follow})

