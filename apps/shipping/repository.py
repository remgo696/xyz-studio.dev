"""
Repositorio de métodos de envío personalizado para XYZ Studio.

Define la lógica de qué métodos de envío están disponibles según:
- La región/departamento de la dirección de envío
- Lima Metropolitana: Envío Estándar (S/9.90) + Envío Urgente (variable)
- Provincias: Envío por Courier (S/16.90)
"""

from decimal import Decimal
from oscar.apps.shipping.repository import Repository as CoreRepository
from oscar.apps.shipping.models import WeightBased
from oscar.apps.shipping.methods import Free, FixedPrice
from oscar.core import prices

# Códigos de departamentos de Lima (incluye Lima y Callao)
LIMA_REGION_CODES = ['PE-LMA', 'PE-LIM', 'PE-CAL', 'LMA', 'LIM', 'CAL', 'LIMA', 'CALLAO']
LIMA_REGION_NAMES = ['lima', 'callao', 'lima metropolitana', 'lima hatun llaqta']


class EnvioUrgenteLima:
    """
    Método de envío urgente para Lima (motorizado).
    
    IMPORTANTE: XYZ Studio NO cobra este envío.
    El cliente paga directamente al motorizado (InDrive, Didi, Rappi, etc.)
    El precio varía según la distancia desde San Juan de Lurigancho.
    """
    code = 'lima-urgente'
    name = 'Envío Urgente (Motorizado)'
    description = 'Entrega el mismo día por motorizado (InDrive/Didi/Rappi)'
    
    # Precio S/0 porque XYZ no cobra, el cliente paga directo al motorizado
    is_discounted = False
    discount = Decimal('0.00')
    
    def calculate(self, basket):
        return prices.Price(
            currency=basket.currency,
            excl_tax=Decimal('0.00'),
            incl_tax=Decimal('0.00')
        )


class Repository(CoreRepository):
    """
    Repositorio personalizado que devuelve métodos de envío según la región.
    """
    
    def get_available_shipping_methods(self, basket, shipping_addr=None, **kwargs):
        """
        Retorna los métodos de envío disponibles según la dirección.
        
        - Sin dirección: Devuelve todos los métodos posibles
        - Lima: Envío Estándar + Envío Urgente
        - Provincias: Solo Envío por Courier
        """
        methods = []
        
        # Determinar si es Lima o Provincia
        is_lima = self._is_lima_address(shipping_addr)
        
        if shipping_addr is None:
            # Sin dirección, mostrar todos los métodos posibles (para preview)
            # Devolver los métodos de Lima por defecto
            is_lima = True
        
        if is_lima:
            # Métodos para Lima Metropolitana
            try:
                lima_standard = WeightBased.objects.get(code='lima-metropolitana-courier')
                methods.append(lima_standard)
            except WeightBased.DoesNotExist:
                # Fallback: crear método fijo
                methods.append(FixedPrice(
                    Decimal('9.90'),
                    code='lima-estandar',
                    name='Envío Estándar Lima'
                ))
            
            # Agregar envío urgente
            methods.append(EnvioUrgenteLima())
        else:
            # Métodos para Provincias
            try:
                provincia = WeightBased.objects.get(code='provincia-courier')
                methods.append(provincia)
            except WeightBased.DoesNotExist:
                # Fallback: crear método fijo
                methods.append(FixedPrice(
                    Decimal('16.90'),
                    code='provincia',
                    name='Envío a Provincia'
                ))
        
        return methods
    
    def _is_lima_address(self, shipping_addr):
        """
        Determina si una dirección es de Lima Metropolitana.
        
        Usa el campo 'state' (departamento/región) para determinar.
        """
        if shipping_addr is None:
            return True  # Por defecto, asumir Lima
        
        # Verificar por el campo state (región/departamento)
        state = getattr(shipping_addr, 'state', '') or ''
        state_lower = state.lower().strip()
        
        # Verificar si es Lima por nombre
        if any(lima_name in state_lower for lima_name in LIMA_REGION_NAMES):
            return True
        
        # Verificar si es Lima por código
        state_upper = state.upper().strip()
        if state_upper in LIMA_REGION_CODES:
            return True
        
        # También verificar el campo line4 (ciudad/distrito) por si acaso
        line4 = getattr(shipping_addr, 'line4', '') or ''
        line4_lower = line4.lower().strip()
        
        # Lista de distritos de Lima
        lima_districts = [
            'miraflores', 'san isidro', 'surco', 'la molina', 'san borja',
            'barranco', 'chorrillos', 'jesús maría', 'jesus maria', 'lince',
            'magdalena', 'pueblo libre', 'breña', 'brena', 'san miguel',
            'cercado', 'lima cercado', 'rimac', 'rímac', 'ate', 'santa anita',
            'el agustino', 'san juan de lurigancho', 'sjl', 'comas', 'independencia',
            'los olivos', 'san martin de porres', 'san martín de porres',
            'carabayllo', 'puente piedra', 'ancon', 'ancón', 'ventanilla',
            'callao', 'la perla', 'bellavista', 'carmen de la legua',
            'villa el salvador', 'villa maría del triunfo', 'san juan de miraflores',
            'surquillo', 'pachacamac', 'lurin', 'lurín', 'cieneguilla', 'chaclacayo',
            'chosica', 'lurigancho', 'punta hermosa', 'punta negra', 'san bartolo',
            'santa maría del mar', 'pucusana', 'chilca'
        ]
        
        if any(district in line4_lower for district in lima_districts):
            return True
        
        return False
