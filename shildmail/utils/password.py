import hashlib
import base64
import re

def generate_dovecot_password(password: str, with_prefix = True) -> str:
    # Zakodowanie hasła na bajty
    password_bytes = password.encode('utf-8')

    # Obliczenie hasha SHA-512
    sha512_hash = hashlib.sha512(password_bytes).digest()

    # Zakodowanie wyniku w Base64
    base64_hash = base64.b64encode(sha512_hash).decode('utf-8')

    if(with_prefix):
        return f"{'{SHA512}'}{base64_hash}"

    return base64_hash


def refine_password_prefix(pass_str: str) -> str:
    """
    Usuwa ciąg znaków w nawiasach klamrowych {.*} z podanego hasła.
    
    :param pass_str: Ciąg wejściowy zawierający hasło z możliwym prefiksem {.*}.
    :return: Oczyszczony ciąg bez prefiksu w nawiasach klamrowych.
    """
    # Usunięcie ciągu w formacie {.*} przy użyciu wyrażenia regularnego
    refined_password = re.sub(r'\{.*?\}', '', pass_str)
    return refined_password