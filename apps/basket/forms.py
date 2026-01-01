# apps/basket/forms.py
import os
from django import forms
from django.core.files.storage import default_storage
from oscar.apps.basket.forms import AddToBasketForm as OriginalAddToBasketForm
from oscar.apps.basket.forms import SimpleAddToBasketMixin #

class AddToBasketForm(OriginalAddToBasketForm):
    def _add_option_field(self, product, option):
        super()._add_option_field(product, option)
        # Verifica el código exacto que obtuviste (ej: 'sube-tu-foto')
        if option.code == 'sube-tu-foto': 
            self.fields[option.code] = forms.ImageField(
                label=option.name,
                required=option.required,
                widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
            )

    def clean(self):
        cleaned_data = super().clean()
        codigo_opcion = 'sube-tu-foto'
        
        if codigo_opcion in cleaned_data:
            imagen = cleaned_data.get(codigo_opcion)
            
            # Si el campo es obligatorio y 'imagen' es una cadena (o está vacío) 
            # en lugar de un objeto de archivo, Django fallará.
            if imagen and hasattr(imagen, 'name'):
                filename = imagen.name
                ruta_relativa = os.path.join('uploads', filename)
                path = default_storage.save(ruta_relativa, imagen)
                cleaned_data[codigo_opcion] = path
        return cleaned_data

class SimpleAddToBasketForm(SimpleAddToBasketMixin, AddToBasketForm):
    pass