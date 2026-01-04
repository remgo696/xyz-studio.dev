from oscar.apps.checkout.views import *

from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from oscar.apps.payment.models import SourceType, Source
from django.shortcuts import redirect

class PaymentDetailsView(CorePaymentDetailsView):
    """
    Sobrescribimos la vista de detalles de pago para omitir la pasarela bancaria
    y permitir un flujo de "Coordinación Manual".
    """
    # Mostrar vista previa antes de confirmar
    preview = True 

    def handle_payment(self, order_number, total, **kwargs):
        # --- LÓGICA DE BYPASS DE PAGO ---
        
        # 1. Definir el método de pago ficticio
        # Esto aparecerá en el Dashboard como el método usado
        source_type, _ = SourceType.objects.get_or_create(
            name='Coordinación Manual (Yape/Plin/Transferencia)'
        )
        
        # 2. Crear el registro de la "fuente" de pago
        # amount_debited=0 es importante porque técnicamente el dinero no ha entrado
        # a tu cuenta bancaria digitalmente aún.
        source = Source(
            source_type=source_type,
            currency=total.currency,
            amount_allocated=total.incl_tax,
            amount_debited=0, 
            reference=order_number
        )
        self.add_payment_source(source)

        # 3. Registrar el evento en el historial del pedido
        self.add_payment_event('Pedido Creado - Pago Pendiente de Confirmación', total.incl_tax)

        # NOTA TÉCNICA:
        # Al no lanzar excepciones (como PaymentError), Oscar asume que el pago
        # fue "exitoso" y procede automáticamente a colocar la orden (place_order).
        return

    # Si necesitas pasar datos extra al template (como el número de Yape)
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['payment_method'] = 'manual'
        return ctx