import oscar.apps.checkout.apps as apps
from oscar.core.loading import get_class

class CheckoutConfig(apps.CheckoutConfig):
    name = 'apps.checkout'
    label = 'checkout'
    verbose_name = 'Checkout'

    def ready(self):
        super().ready()
        # Esto le dice a Oscar: "Cuando busques PaymentDetailsView, usa LA MÍA"
        self.payment_details_view = get_class('checkout.views', 'PaymentDetailsView')