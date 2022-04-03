from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout as django_logout
from .forms import UserRegisterForm
from stats.models import Game


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Bem vindo {username}! Já pode fazer o seu login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required()
def profile(request):
    return render(request, 'users/profile.html')

@login_required
def logout(request, **kwargs):
    messages.success(request, 'Logged out.')
    django_logout(request)
    return redirect('stats-home')

@login_required
def add(request, game_id):
    Game(game_id=game_id, user=request.user).save()
    messages.success(request, 'Jogo adicionado.')
    return redirect('stats-home')

