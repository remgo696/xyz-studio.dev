"""
Context processors personalizados para XYZ Studio.

Expone variables de configuración a todos los templates automáticamente.
"""

from django.conf import settings


def shop_info(request):
    """
    Inyecta información de contacto y pago de XYZ Studio en todos los templates.
    """
    return {
        # Contacto público
        'shop_whatsapp': getattr(settings, 'SHOP_WHATSAPP', '51999999999'),
        'shop_whatsapp_display': getattr(settings, 'SHOP_PHONE', '999 999 999'),
        'shop_email': getattr(settings, 'SHOP_EMAIL', 'contacto@xyzstudio.pe'),
        'shop_phone': getattr(settings, 'SHOP_PHONE', '999999999'),
        'shop_address': getattr(settings, 'SHOP_ADDRESS', 'Lima, Perú'),
        
        # Redes sociales
        'shop_instagram': getattr(settings, 'SHOP_INSTAGRAM', ''),
        'shop_tiktok': getattr(settings, 'SHOP_TIKTOK', ''),
        'shop_linkedin': getattr(settings, 'SHOP_LINKEDIN', ''),
        
        # Datos bancarios (solo mostrar en páginas de pago)
        'shop_bank_bcp_account': getattr(settings, 'BANK_BCP_ACCOUNT', ''),
        'shop_bank_bcp_cci': getattr(settings, 'BANK_BCP_CCI', ''),
        'shop_bank_bcp_holder': getattr(settings, 'BANK_BCP_HOLDER', ''),
        
        # Yape / Plin
        'shop_yape_phone': getattr(settings, 'YAPE_PHONE', ''),
        'shop_yape_holder': getattr(settings, 'YAPE_HOLDER', ''),
        'shop_plin_phone': getattr(settings, 'PLIN_PHONE', ''),

        # Datos legales
        'shop_legal_name': getattr(settings, 'LEGAL_NAME', ''),
        'shop_legal_ruc': getattr(settings, 'LEGAL_RUC', ''),
    }
