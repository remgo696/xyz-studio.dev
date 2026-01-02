from django import forms
from oscar.apps.basket.forms import AddToBasketForm as OriginalAddToBasketForm

class AddToBasketForm(OriginalAddToBasketForm):
    
    def _add_option_field(self, product, option):
        super()._add_option_field(product, option)
        
        # 1. Configuración para Subida de Fotos
        if option.code == 'sube-tu-foto': 
            self.fields[option.code].widget.attrs.update({
                'class': 'file-dropzone',
                'accept': 'image/*'
            })

        # 2. Configuración para Colores (Radio Buttons)
        elif 'color' in option.code.lower():
            # Cambiamos el widget por defecto (Select) a RadioSelect
            self.fields[option.code].widget = forms.RadioSelect(attrs={
                'class': 'color-swatch-list'
            })