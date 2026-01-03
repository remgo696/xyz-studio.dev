import oscar.apps.checkout.apps as apps
from django.urls import path
from oscar.core.loading import get_class

class CheckoutConfig(apps.CheckoutConfig):
    name = 'apps.checkout'
    
    def ready(self):
        super().ready()
        # Cargamos nuestra vista personalizada
        self.payment_details_view = get_class('checkout.views', 'PaymentDetailsView')