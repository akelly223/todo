"""
Vues pour l'authentification des utilisateurs.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def register(request):
    """
    Vue pour l'inscription d'un nouvel utilisateur.
    """
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            # Connexion automatique après inscription
            login(request, user)
            
            messages.success(request, f'🎉 Bienvenue {username} ! Votre compte a été créé avec succès.')
            return redirect('tasks:dashboard')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'users/register.html', context)


def user_login(request):
    """
    Vue pour la connexion d'un utilisateur.
    """
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'👋 Bon retour, {username} !')
                
                # Redirection vers la page demandée ou dashboard
                next_page = request.GET.get('next', 'tasks:dashboard')
                return redirect(next_page)
        else:
            messages.error(request, '❌ Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'users/login.html', context)


@login_required
def user_logout(request):
    """
    Vue pour la déconnexion d'un utilisateur.
    """
    username = request.user.username
    logout(request)
    messages.success(request, f'👋 À bientôt, {username} !')
    return redirect('users:login')
