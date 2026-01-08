import os
from django import forms
from django.core.files.storage import default_storage
from oscar.apps.basket.forms import AddToBasketForm as OriginalAddToBasketForm
from oscar.apps.basket.forms import SimpleAddToBasketMixin

class AddToBasketForm(OriginalAddToBasketForm):
    
    def _add_option_field(self, product, option):
        """
        Sobrescribimos este método para inyectar nuestros widgets personalizados
        (Dropzone para archivos y Swatches para colores).
        """
        # 1. Ejecutamos la lógica original para que Oscar prepare el terreno
        super()._add_option_field(product, option)
        
        # 2. PERSONALIZACIÓN: Subida de Foto (Reemplazo total del campo)
        if option.code == 'sube-tu-foto': 
            # Es vital definirlo como ImageField aquí para que Django acepte archivos
            self.fields[option.code] = forms.ImageField(
                label=option.name,
                required=option.required,
                widget=forms.ClearableFileInput(attrs={
                    'accept': 'image/*',
                    'class': 'file-dropzone' # Clase para el diseño CSS
                })
            )

        # 3. PERSONALIZACIÓN: Colores (Cambio de widget a Radio)
        elif 'color' in option.code.lower():
            self.fields[option.code].widget = forms.RadioSelect(attrs={
                'class': 'color-swatch-list' # Clase para convertir radios en círculos
            })
        
        # 4. PERSONALIZACIÓN: Texto personalizado (Límite de 15 caracteres)
        elif 'texto-personalizado' in option.code.lower():
            self.fields[option.code].max_length = 15
            if self.fields[option.code].widget.attrs:
                self.fields[option.code].widget.attrs['maxlength'] = 15
            else:
                self.fields[option.code].widget.attrs = {'maxlength': 15}

    def clean(self):
        """
        Lógica para guardar el archivo físico en el disco cuando se envía el form.
        """
        cleaned_data = super().clean()
        codigo_opcion = 'sube-tu-foto'
        
        if codigo_opcion in cleaned_data:
            imagen = cleaned_data.get(codigo_opcion)
            
            # Verificamos si es un archivo real que necesita guardarse
            if imagen and hasattr(imagen, 'name'):
                filename = imagen.name
                # Guardamos en media/uploads/...
                ruta_relativa = os.path.join('uploads', filename)
                
                # Esto guarda el archivo físicamente
                path = default_storage.save(ruta_relativa, imagen)
                
                # Actualizamos el dato para que en la BD se guarde solo la ruta (texto)
                cleaned_data[codigo_opcion] = path
                
        return cleaned_data

class SimpleAddToBasketForm(SimpleAddToBasketMixin, AddToBasketForm):
    """
    Versión simplificada para las vistas de catálogo (botones pequeños).
    Al heredar de NUESTRO AddToBasketForm, también gana los estilos y correcciones.
    """
    pass