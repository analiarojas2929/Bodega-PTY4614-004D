from datetime import datetime
from django.utils.timezone import make_aware

def format_date(fecha_str):
    """
    Convierte una cadena de fecha en un objeto datetime con zona horaria.
    Intenta con distintos formatos.
    """
    formatos = ['%Y-%m-%d', '%d-%m-%Y']
    for formato in formatos:
        try:
            fecha = datetime.strptime(fecha_str, formato)
            return make_aware(fecha)
        except ValueError:
            continue
    return None
