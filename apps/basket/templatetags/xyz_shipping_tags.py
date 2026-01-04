from django import template
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache

register = template.Library()


def get_free_shipping_threshold():
    """
    Obtiene el umbral de envío gratis desde las ofertas de Oscar.
    Busca una oferta activa con beneficio de envío gratis y retorna
    el valor mínimo de la condición.
    
    Cachea el resultado por 5 minutos para evitar consultas repetidas.
    """
    cache_key = 'free_shipping_threshold'
    threshold = cache.get(cache_key)
    
    if threshold is None:
        try:
            from oscar.apps.offer.models import ConditionalOffer, Benefit
            from django.utils import timezone
            
            # Buscar ofertas activas con beneficio de envío
            now = timezone.now()
            offers = ConditionalOffer.objects.filter(
                offer_type=ConditionalOffer.SITE,
                status=ConditionalOffer.OPEN,
                start_datetime__lte=now,
            ).filter(
                # Ofertas sin fecha de fin o con fecha de fin futura
            ).select_related('condition', 'benefit')
            
            for offer in offers:
                # Verificar si el beneficio es de tipo envío gratis
                if offer.benefit.type == Benefit.SHIPPING_FIXED_PRICE and offer.benefit.value == 0:
                    # Obtener el valor mínimo de la condición
                    if hasattr(offer.condition, 'value') and offer.condition.value:
                        threshold = Decimal(str(offer.condition.value))
                        break
                elif offer.benefit.type == Benefit.SHIPPING_PERCENTAGE and offer.benefit.value == 100:
                    if hasattr(offer.condition, 'value') and offer.condition.value:
                        threshold = Decimal(str(offer.condition.value))
                        break
            
        except Exception:
            pass
        
        # Si no encontramos oferta, usar valor por defecto de settings o 490
        if threshold is None:
            threshold = Decimal(str(getattr(settings, 'FREE_SHIPPING_THRESHOLD', 490)))
        
        # Cachear por 5 minutos
        cache.set(cache_key, threshold, 300)
    
    return threshold


@register.simple_tag
def free_shipping_threshold():
    """
    Retorna el umbral de envío gratis para usar en templates.
    Ejemplo: {% free_shipping_threshold as threshold %}
    """
    return get_free_shipping_threshold()


@register.simple_tag
def calculate_shipping_progress(basket, threshold=None):
    """
    Calcula cuánto falta para el envío gratis.
    
    El umbral se obtiene automáticamente de:
    1. Ofertas activas de envío gratis en Oscar Dashboard
    2. settings.FREE_SHIPPING_THRESHOLD
    3. Valor por defecto: 490
    
    Retorna un diccionario con los datos listos para usar.
    """
    # Obtener el threshold dinámicamente si no se especifica
    if threshold is None:
        limit = get_free_shipping_threshold()
    else:
        limit = Decimal(str(threshold))
    
    # 1. Obtener el total actual (con impuestos)
    if not basket or basket.is_empty:
        total = Decimal('0.00')
    else:
        # Usamos total_incl_tax si existe, sino 0
        total = basket.total_incl_tax or Decimal('0.00')
    
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