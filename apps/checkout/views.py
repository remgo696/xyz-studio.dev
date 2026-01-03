from django import forms
from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from oscar.apps.payment.models import SourceType, Source


class PaymentDetailsView(CorePaymentDetailsView):
    # Ocultamos el formularsio de previsualización para ir directo al grano
    preview = False

    def handle_payment(self, order_number, total, **kwargs):
        # 1. Definir el método de pago ficticio
        source_type, _ = SourceType.objects.get_or_create(
            name='Coordinación Manual (Yape/Plin/Transferencia)'
        )

        # 2. Registrar la "intención" de pago (Suma 0 cobrada real)
        source = Source(
            source_type=source_type,
            currency=total.currency,
            amount_allocated=total.incl_tax,
            amount_debited=0,  # 0 porque no hemos cobrado online
            reference=order_number,
        )
        self.add_payment_source(source)

        # 3. Registrar evento
        self.add_payment_event('Pedido Creado - Pago Pendiente', total.incl_tax)
        # Si no lanzamos excepciones, Oscar asume éxito y crea la orden
