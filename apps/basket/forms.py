import os
from django import forms
from django.conf import settings
from django.core.files.storage import default_storage
from oscar.apps.basket.forms import AddToBasketForm as OriginalAddToBasketForm

class AddToBasketForm(OriginalAddToBasketForm):
    
    # SOBRESCRIBIMOS ESTE MÉTODO ESPECÍFICO (Línea 232 de tu archivo original)
    def _add_option_field(self, product, option):
        """
        Dejamos que Oscar cree el campo normalmente, y si es el de la foto,
        lo reemplazamos por un campo de archivo.
        """
        # 1. Ejecutar lógica original (crea el campo de texto)
        super()._add_option_field(product, option)
        
        # 2. Intervenir si es nuestra opción
        # REEMPLAZA 'sube-tu-foto' con el código que viste en el paso 1
        if option.code == 'sube-tu-foto': 
            self.fields[option.code] = forms.ImageField(
                label=option.name,
                required=option.required,
                widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
            )

    # Mantenemos la lógica de limpieza para guardar el archivo
    def clean(self):
        cleaned_data = super().clean()
        
        # REEMPLAZA AQUÍ TAMBIÉN EL CÓDIGO
        codigo_opcion = 'sube-tu-foto'
        
        if codigo_opcion in cleaned_data:
            imagen = cleaned_data.get(codigo_opcion)
            
            # Si es un archivo real (tiene nombre y contenido)
            if imagen and hasattr(imagen, 'name'):
                # Definir ruta: media/uploads/2025/...
                filename = imagen.name
                ruta_relativa = os.path.join('uploads', filename)
                
                # Guardar físico
                path = default_storage.save(ruta_relativa, imagen)
                
                # Reemplazar el objeto archivo por la ruta (string) para la BD
                cleaned_data[codigo_opcion] = path
                
        return cleaned_data