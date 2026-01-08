"""
Formularios de checkout personalizados para XYZ Studio.
"""

from oscar.apps.checkout.forms import (
    ShippingAddressForm as OscarShippingAddressForm,
    ShippingMethodForm,
    GatewayForm
)
from apps.address.forms import ShippingAddressForm


# Re-exportar todos los formularios requeridos por Oscar                                
__all__ = ['ShippingAddressForm', 'ShippingMethodForm', 'GatewayForm']
