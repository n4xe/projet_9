from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    pass


class Ticket(models.Model):
    title = models.CharField("Titre", max_length=128)
    description = models.TextField("Description", max_length=2048, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def get_model_name(self):
        return "Ticket"

    def has_review(self):
        return self.review_set.exists()


class Review(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    headline = models.CharField("Titre", max_length=128)
    rating = models.PositiveSmallIntegerField("Evaluation",
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    body = models.TextField("Critique", max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.ticket.title}"

    def get_model_name(self):
        return "Review"


class UserFollows(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_by')

    class Meta:
        unique_together = ('user', 'followed_user',)


class UserBlock(models.Model):
    # L'utilisateur qui effectue le blocage
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='blocking',
        on_delete=models.CASCADE
    )
    # L'utilisateur qui est bloqué
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='blocked_by',
        on_delete=models.CASCADE
    )
    # Date et heure du blocage
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked',)

    def __str__(self):
        return f"{self.blocker.username} blocks {self.blocked.username}"
