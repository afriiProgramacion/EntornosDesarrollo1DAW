import re

def validar_email(email):
    if "@" not in email:
        return False

    if email.startswith("@") or email.endswith("@"):
        return False

    if not (email.endswith(".com") or email.endswith(".es") or email.endswith(".org")):
        return False

    return True

def validar_telefono(tel):
    return tel.isdigit() and len(tel) == 9