from django import template
from decimal import Decimal

register = template.Library()

@register.simple_tag
def calculate_shipping_progress(basket, threshold=490):
    """
    Calcula cuánto falta para el envío gratis (S/ 490).
    Retorna un diccionario con los datos listos para usar.
    """
    # 1. Obtener el total actual (con impuestos)
    if not basket or basket.is_empty:
        total = Decimal('0.00')
    else:
        # Usamos total_incl_tax si existe, sino 0
        total = basket.total_incl_tax or Decimal('0.00')

    # 2. Convertir threshold a Decimal para operar
    limit = Decimal(str(threshold))
    
    # 3. Calcular la brecha (Gap)
    gap = limit - total
    
    # 4. Calcular el porcentaje (0 a 100)
    if total >= limit:
        percent = 100
        gap = 0
    else:
        percent = (total / limit) * 100

    return {
        'total': total,
        'limit': limit,
        'gap': gap,
        'percent': round(percent, 1), # Redondeamos para CSS
        'is_free': total >= limit
    }