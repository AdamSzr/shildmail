from django.shortcuts import redirect
from functools import wraps

def check_device_id(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Sprawdź, czy w sesji jest klucz 'device_id'
        if 'device_id' in request.session:
            # Sprawdz czy user posiada taki device id
            return view_func(request, *args, **kwargs)  # Procesuj widok dalej
        else:
            return redirect('/2fa')  # Przekieruj na stronę autoryzacji urządzenia
    return wrapper
