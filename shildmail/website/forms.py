from django import forms

from shildmail.models.user import User

from django.core.exceptions import ValidationError
class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Email', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = "{PLAIN}"+ cleaned_data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid email or password")

        if user.password != password:  # Porównanie plaintext
            raise forms.ValidationError("Invalid email or password")

        cleaned_data['user'] = user
        return cleaned_data



class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        label="Nazwa użytkownika"
    )
    realname = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Real Name'}),
        label="Imię i nazwisko"
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label="Hasło"
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        username = f"{username}@adamszreiber.pl"

        return username

    # def clean_realname(self):
    #     realname = self.cleaned_data.get('realname')
    #     if realname:
    #         realname = realname.lower().replace(' ', '_') + '/'
    #     return realname

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return f"{'{PLAIN}'}{password}"

    def clean(self):
        # W razie potrzeby możesz dodać ogólną walidację między polami tutaj.
        return super().clean()



class MailForm(forms.Form):
    to = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Adresat'}),
        label="Do"
    )
    subject = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Temat'}),
        label="Temat"
    )
    content = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Treść'}),
        label="Wiadomość"
    )
