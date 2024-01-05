from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm


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
