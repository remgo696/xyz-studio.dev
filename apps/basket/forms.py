import os
from django import forms
from django.core.files.storage import default_storage
from oscar.apps.basket.forms import AddToBasketForm as OriginalAddToBasketForm
from oscar.apps.basket.forms import SimpleAddToBasketMixin

class AddToBasketForm(OriginalAddToBasketForm):
    
    def _add_option_field(self, product, option):
        super()._add_option_field(product, option)
        
        # 1. LÓGICA PARA SUBIR FOTO
        if option.code == 'sube-tu-foto': 
            self.fields[option.code] = forms.ImageField(
                label=option.name,
                required=option.required,
                widget=forms.ClearableFileInput(attrs={
                    'accept': 'image/*',
                    'class': 'file-dropzone'  # <--- INYECCIÓN DE CLASE CSS
                })
            )

        # 2. LÓGICA PARA COLORES (Swatches)
        # Detectamos si es color por el código o nombre
        elif 'color' in option.code.lower() or 'colour' in option.code.lower():
            self.fields[option.code].widget = forms.RadioSelect(attrs={
                'class': 'color-swatch-list' # <--- INYECCIÓN DE CLASE CSS
            })
            
    def clean(self):
        cleaned_data = super().clean()
        codigo_opcion = 'sube-tu-foto'
        
        if codigo_opcion in cleaned_data:
            imagen = cleaned_data.get(codigo_opcion)
            if imagen and hasattr(imagen, 'name'):
                filename = imagen.name
                ruta_relativa = os.path.join('uploads', filename)
                path = default_storage.save(ruta_relativa, imagen)
                cleaned_data[codigo_opcion] = path
        return cleaned_data

class SimpleAddToBasketForm(SimpleAddToBasketMixin, AddToBasketForm):
    pass