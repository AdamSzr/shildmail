from django.shortcuts import redirect
from functools import wraps
from shildmail.settings import APP_MODE

def webauthn_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Sprawdź, czy w sesji jest klucz 'device_id'

        is_webauthn = True if APP_MODE == 'dev' else 'credential_id' in request.session
        if is_webauthn:
            # Sprawdz czy user posiada taki device id
            return view_func(request, *args, **kwargs)  # Procesuj widok dalej
        else:
            return redirect('second-factor-authentication')  # Przekieruj na stronę autoryzacji urządzenia
    return wrapper
