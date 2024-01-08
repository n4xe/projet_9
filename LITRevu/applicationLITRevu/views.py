from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import Ticket, Review, UserFollows
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from itertools import chain
from operator import attrgetter
import logging

logger = logging.getLogger(__name__)

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
def create_review(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.debug(request, f'Ticket {ticket.id} created by {request.user.username}')

            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            messages.debug(request, f'Review {review.id} created for ticket {ticket.id} by {request.user.username}')

            return redirect('feed')
            logger.debug(f'Ticket {ticket.id} created by {request.user.username}')
            logger.debug(f'Review {review.id} created for ticket {ticket.id} by {request.user.username}')
        else:
            messages.error(request, 'There was an error with the form.')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    context = {
        'ticket_form': ticket_form,
        'review_form': review_form
    }
    return render(request, 'create_review.html', context)

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
            return redirect('feed')
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
            return redirect('feed/')
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
    follows = UserFollows.objects.filter(user=request.user)
    followers = UserFollows.objects.filter(followed_user=request.user)
    form = UserFollowForm()

    if request.method == 'POST':
        form = UserFollowForm(request.POST)
        if form.is_valid():
            username_to_follow = form.cleaned_data['username']
            try:
                followed_user = User.objects.get(username=username_to_follow)
                if followed_user != request.user:
                    UserFollows.objects.get_or_create(user=request.user, followed_user=followed_user)
                    messages.success(request, "L'utilisateur a bien été ajouté.")
                else:
                    messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
            except User.DoesNotExist:
                messages.error(request, "L'utilisateur saisi n'existe pas.")
        else:
            messages.error(request, "Le formulaire n'est pas valide.")

    return render(request, 'user_follows.html', {
        'follows': follows,
        'followers': followers,
        'form': form
    })

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


@login_required
def feed(request):
    # Billets et avis de l'utilisateur connecté
    user_tickets = Ticket.objects.filter(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)

    # Utilisateurs suivis par l'utilisateur connecté
    followed_users = UserFollows.objects.filter(user=request.user).values_list('followed_user', flat=True)

    # Billets et avis des utilisateurs suivis
    followed_tickets = Ticket.objects.filter(user__in=followed_users)
    followed_reviews = Review.objects.filter(user__in=followed_users)

    # Avis en réponse aux billets de l'utilisateur connecté qui ne sont pas déjà comptés dans user_reviews
    responses_to_user_tickets = Review.objects.filter(ticket__in=user_tickets).exclude(
        id__in=user_reviews.values_list('id', flat=True))

    # Combinez les requêtes et ordonnez-les par date de création (les plus récents en premier)
    feed_items = sorted(
        chain(user_tickets, user_reviews, followed_tickets, followed_reviews, responses_to_user_tickets),
        key=attrgetter('time_created'),
        reverse=True
    )
    for item in feed_items:
        if hasattr(item, 'rating'):  # Vérifiez si l'item a un attribut 'rating'
            # Créez des listes d'étoiles pleines et vides
            item.stars_full = [None] * item.rating  # Une liste avec des Nones pour chaque étoile pleine
            item.stars_empty = [None] * (5 - item.rating)  # Une liste avec des Nones pour chaque étoile vide

    return render(request, 'feed.html', {'feed_items': feed_items})

@login_required
def posts(request):
    user_tickets = Ticket.objects.filter(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)

    return render(request, 'posts.html', {
        'user_tickets': user_tickets,
        'user_reviews': user_reviews
    })