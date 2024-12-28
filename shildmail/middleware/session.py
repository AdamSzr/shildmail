def display_session_id(get_response):
    def middleware(request):
        return get_response(request)

    return middleware