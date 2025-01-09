from django.shortcuts import redirect
from functools import wraps

def webauthn_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Sprawdź, czy w sesji jest klucz 'device_id'
        if 'credential_id' in request.session:
            # Sprawdz czy user posiada taki device id
            return view_func(request, *args, **kwargs)  # Procesuj widok dalej
        else:
            return redirect('second-factor-authentication')  # Przekieruj na stronę autoryzacji urządzenia
    return wrapper
