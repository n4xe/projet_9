from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from itertools import chain
from operator import attrgetter
from .forms import CustomUserCreationForm, TicketForm, ReviewForm, UserFollowForm, User
from .models import Ticket, Review, UserFollows, UserBlock
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
            return redirect('feed')  # Assume you have a 'feed' view to redirect to
    else:
        form = TicketForm()  # This form will be used for GET requests or POST requests that are not valid

    # Now 'form' is passed to the template whether it's a fresh one or one with errors from an invalid POST
    return render(request, 'ticket.html', {'form': form})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'ticket.html', {'form': form})


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Ticket supprimé")
        return redirect('posts')
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
            return redirect('posts')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'review_form.html', {'form': form, 'ticket': review.ticket})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Critique supprimée")
        return redirect('posts')  # Ou toute autre vue de redirection
    return render(request, 'review_confirm_delete.html', {'review': review})


@login_required
def user_follows(request):
    # Récupérer les IDs des utilisateurs bloqués
    blocked_users_ids = UserBlock.objects.filter(blocker=request.user).values_list('blocked', flat=True)

    # Abonnements, excluant les utilisateurs bloqués
    follows = UserFollows.objects.filter(user=request.user).exclude(followed_user__in=blocked_users_ids)

    # Abonnés, excluant les utilisateurs bloqués
    followers = UserFollows.objects.filter(followed_user=request.user).exclude(user__in=blocked_users_ids)

    # Utilisateurs bloqués
    blocked_users = User.objects.filter(id__in=blocked_users_ids)

    form = UserFollowForm()
    if request.method == 'POST':
        form = UserFollowForm(request.POST)
        if form.is_valid():
            username_to_follow = form.cleaned_data['username']
            try:
                followed_user = User.objects.get(username=username_to_follow)
                if followed_user != request.user:
                    if UserFollows.objects.filter(user=request.user, followed_user=followed_user).exists():
                        messages.error(request, "Vous suivez déjà cet utilisateur.")
                    elif UserBlock.objects.filter(blocker=request.user, blocked=followed_user).exists():
                        messages.error(request, "Vous avez bloqué cet utilisateur.")
                    else:
                        UserFollows.objects.create(user=request.user, followed_user=followed_user)
                        messages.success(request, "Utilisateur suivi avec succès.")
                else:
                    messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
            except User.DoesNotExist:
                messages.error(request, "L'utilisateur saisi n'existe pas.")
        else:
            form = UserFollowForm()  # Réinitialiser le formulaire après la soumission

    return render(request, 'user_follows.html', {
        'follows': follows,
        'followers': followers,
        'blocked_users': blocked_users,
        'form': form
    })


@login_required
def follow_user(request):
    if request.method == 'POST':
        form = UserFollowForm(request.POST)
        if form.is_valid():
            username_to_follow = form.cleaned_data['username']
            try:
                followed_user = User.objects.get(username=username_to_follow)
                if followed_user != request.user:
                    # Vérifier si l'utilisateur est déjà suivi
                    if UserFollows.objects.filter(user=request.user, followed_user=followed_user).exists():
                        messages.info(request, "Vous êtes déjà abonné à cet utilisateur.")
                    else:
                        # Créer l'abonnement si il n'existe pas déjà
                        UserFollows.objects.create(user=request.user, followed_user=followed_user)
                        messages.success(request, "Vous vous êtes abonné avec succès.")
                else:
                    messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
            except User.DoesNotExist:
                messages.error(request, "L'utilisateur saisi n'existe pas.")
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

    # Utilisateurs qui ont bloqué ou ont été bloqués par l'utilisateur connecté
    blocked_users = UserBlock.objects.filter(Q(blocked=request.user) | Q(blocker=request.user)).values_list('blocked',
                                                                                                            flat=True)

    # Billets et avis des utilisateurs suivis, en excluant les utilisateurs bloqués
    followed_tickets = Ticket.objects.filter(user__in=followed_users).exclude(user__in=blocked_users)
    followed_reviews = Review.objects.filter(user__in=followed_users).exclude(user__in=blocked_users)

    # Avis en réponse aux billets de l'utilisateur connecté qui ne sont pas déjà comptés dans user_reviews
    responses_to_user_tickets = Review.objects.filter(ticket__in=user_tickets).exclude(
        id__in=user_reviews.values_list('id', flat=True)).exclude(user__in=blocked_users)

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
    user_tickets = Ticket.objects.filter(user=request.user).order_by('-time_created')
    user_reviews = Review.objects.filter(user=request.user).order_by('-time_created')

    # Combine les tickets et les reviews en une seule liste
    user_posts = sorted(
        chain(user_tickets, user_reviews),
        key=attrgetter('time_created'),
        reverse=True  # Tri décroissant pour obtenir les plus récents en premier
    )

    return render(request, 'posts.html', {'user_posts': user_posts})


@login_required
def block_user(request, user_id):
    user_to_block = get_object_or_404(User, pk=user_id)
    UserBlock.objects.create(blocker=request.user, blocked=user_to_block)
    # Redirigez l'utilisateur vers la page appropriée après le blocage
    return redirect('user_follows')


@login_required
def unblock_user(request, user_id):
    # Récupérer l'instance UserBlock et la supprimer
    UserBlock.objects.filter(blocker=request.user, blocked__id=user_id).delete()
    # Redirection vers la page d'abonnements
    return redirect('user_follows')
