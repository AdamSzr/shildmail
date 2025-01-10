from django import template
from django.http import QueryDict

register = template.Library()

@register.filter
def remove_message_id(query_string):
    """Usuwa istniejące parametry `message_id` z query_string."""
    if not query_string:
        return ""
    query_dict = QueryDict(query_string, mutable=True)
    query_dict.pop("message_id", None)  # Usuwamy wszystkie `message_id`
    return query_dict.urlencode()

@register.filter
def remove_mailbox(query_string):
    """Usuwa istniejące parametry `message_id` z query_string."""
    if not query_string:
        return ""
    query_dict = QueryDict(query_string, mutable=True)
    query_dict.pop("mailbox", None)
    query_dict.pop('message_id',None)
    return query_dict.urlencode()