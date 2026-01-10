"""
Formularios de dirección personalizados para XYZ Studio.

Usa pycountry para listar los departamentos del Perú.
"""

from django import forms
from django.utils.translation import gettext_lazy as _
import pycountry

from oscar.apps.address.forms import UserAddressForm as CoreUserAddressForm


def get_peru_regions_choices():
    """
    Obtiene la lista de departamentos/regiones de Perú usando pycountry.
    Retorna una lista de tuplas (código, nombre) ordenada alfabéticamente.
    """
    choices = [('', '-- Selecciona un departamento --')]
    
    try:
        peru_subdivisions = list(pycountry.subdivisions.get(country_code='PE'))
        
        # Ordenar por nombre y agregar al listado
        sorted_regions = sorted(peru_subdivisions, key=lambda x: x.name)
        
        for region in sorted_regions:
            # Normalizar nombres para mejor legibilidad
            name = region.name
            # Convertir "Lima hatun llaqta" a "Lima Metropolitana"
            if 'hatun llaqta' in name.lower():
                name = 'Lima Metropolitana'
            elif 'Amarumayu' in name:
                name = 'Amazonas'
            
            choices.append((region.code, name))
    except Exception:
        # Fallback: lista manual de departamentos
        departments = [
            ('PE-AMA', 'Amazonas'),
            ('PE-ANC', 'Áncash'),
            ('PE-APU', 'Apurímac'),
            ('PE-ARE', 'Arequipa'),
            ('PE-AYA', 'Ayacucho'),
            ('PE-CAJ', 'Cajamarca'),
            ('PE-CAL', 'Callao'),
            ('PE-CUS', 'Cusco'),
            ('PE-HUV', 'Huancavelica'),
            ('PE-HUC', 'Huánuco'),
            ('PE-ICA', 'Ica'),
            ('PE-JUN', 'Junín'),
            ('PE-LAL', 'La Libertad'),
            ('PE-LAM', 'Lambayeque'),
            ('PE-LIM', 'Lima'),
            ('PE-LMA', 'Lima Metropolitana'),
            ('PE-LOR', 'Loreto'),
            ('PE-MDD', 'Madre de Dios'),
            ('PE-MOQ', 'Moquegua'),
            ('PE-PAS', 'Pasco'),
            ('PE-PIU', 'Piura'),
            ('PE-PUN', 'Puno'),
            ('PE-SAM', 'San Martín'),
            ('PE-TAC', 'Tacna'),
            ('PE-TUM', 'Tumbes'),
            ('PE-UCA', 'Ucayali'),
        ]
        choices.extend(departments)
    
    return choices


class PeruAddressFormMixin:
    """
    Mixin que personaliza los campos de dirección para Perú.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Convertir el campo state (departamento) en un select
        if 'state' in self.fields:
            self.fields['state'] = forms.ChoiceField(
                choices=get_peru_regions_choices(),
                label=_('Departamento'),
                required=True,
                widget=forms.Select(attrs={
                    'class': 'form-control'
                })
            )
        
        # Personalizar labels para Perú
        field_labels = {
            'first_name': _('Nombres'),
            'last_name': _('Apellidos'),
            'line1': _('Dirección'),
            'line2': _('Referencia (opcional)'),
            'line4': _('Distrito'),
            'state': _('Departamento'),
            'postcode': _('Código postal (opcional)'),
            'phone_number': _('Celular'),
            'notes': _('Notas para el courier'),
        }
        
        for field_name, label in field_labels.items():
            if field_name in self.fields:
                self.fields[field_name].label = label
        
        # Hacer algunos campos opcionales
        if 'postcode' in self.fields:
            self.fields['postcode'].required = False
        if 'line2' in self.fields:
            self.fields['line2'].required = False


class UserAddressForm(PeruAddressFormMixin, CoreUserAddressForm):
    """
    Formulario de dirección de usuario con departamentos de Perú.
    """
    pass


def __getattr__(name):
    """
    Lazy import para ShippingAddressForm para evitar circular imports.
    Oscar carga checkout.forms que intenta cargar address.forms,
    pero address.forms no puede importar de checkout.forms directamente.
    """
    if name == "ShippingAddressForm":
        from oscar.apps.checkout.forms import ShippingAddressForm as CoreShippingAddressForm
        
        class ShippingAddressForm(PeruAddressFormMixin, CoreShippingAddressForm):
            """
            Formulario de dirección de envío con departamentos de Perú.
            """
            pass
        
        return ShippingAddressForm
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
