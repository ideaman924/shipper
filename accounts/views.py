from django.contrib.auth import logout
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetConfirmView
from django.shortcuts import render
from rest_framework.authtoken.models import Token

from .forms import *


class PasswordChange(PasswordChangeView):
    def form_valid(self, form):
        # Invalidate tokens for the user
        Token.objects.filter(user=form.user).delete()
        return super().form_valid(form)


class PasswordChangeDone(PasswordChangeDoneView):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return super().get(request, *args, **kwargs)


class PasswordResetConfirm(PasswordResetConfirmView):
    def form_valid(self, form):
        # Invalidate tokens for the user
        Token.objects.filter(user=form.user).delete()
        return super().form_valid(form)


def register(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.is_active = False
            new_user.save()
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = RegisterForm()

    return render(request, 'registration/register.html', {'form': user_form})
