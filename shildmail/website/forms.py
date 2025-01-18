from django import forms

from shildmail.models.user import User

from django.core.exceptions import ValidationError
class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': '', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '', 'class': 'form-control'})
    )

    def clean_email(self):
        username = self.cleaned_data.get('email')
        postfix = '@adamszreiber.pl'

        # Sprawdzenie i dodanie postfixu, jeśli go brak
        if not username.endswith(postfix):
            username += postfix

        return username



class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '','class': 'form-control'}),
        label="Nazwa użytkownika"
    )

    realname = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '','class': 'form-control'}),
        label="Imię i nazwisko"
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': '','class': 'form-control'}),
        label="Hasło"
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        postfix = '@adamszreiber.pl'

        # Sprawdzenie i dodanie postfixu, jeśli go brak
        if not username.endswith(postfix):
            username += postfix

        return username



class MailForm(forms.Form):
    to = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Adresat','class': 'form-control'}),
        label="Do"
    )
    subject = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Temat','class': 'form-control'}),
        label="Temat"
    )
    content = forms.CharField(
        required=True,
        label="Wiadomość",
        widget= forms.Textarea(attrs={
            'rows': 5,
            'cols': 40,
            'placeholder': 'Wprowadź opis...',
            'class': 'form-control'
        }),
    )
