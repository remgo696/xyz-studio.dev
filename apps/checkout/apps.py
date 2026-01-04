import oscar.apps.checkout.apps as apps
from oscar.core.loading import get_class

class CheckoutConfig(apps.CheckoutConfig):
    name = 'apps.checkout'
    label = 'checkout'
    verbose_name = 'Checkout'

    def ready(self):
        super().ready()
        # Usar nuestra vista de pago personalizada
        self.payment_details_view = get_class('checkout.views', 'PaymentDetailsView')
        # Usar nuestro formulario de dirección personalizado
        self.shipping_address_form_class = get_class('checkout.forms', 'ShippingAddressForm')