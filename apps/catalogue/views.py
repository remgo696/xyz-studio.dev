from django.db.models import Q
from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')

class ProductDetailView(CoreProductDetailView):
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object

        # 1. BÚSQUEDA DE HERMANOS (SIBLINGS)
        # Buscamos el atributo 'group_code' para conectar productos independientes.
        # Esto permite que "Lámpara Roja" y "Lámpara Azul" se conozcan entre sí.
        target_attr_code = 'group_code' 
        
        # Obtenemos el valor del grupo del producto actual
        group_value = None
        for av in product.attribute_values.all():
            if av.attribute.code == target_attr_code:
                # Oscar guarda valores en campos distintos según el tipo (text, selection, etc)
                group_value = av.value
                break
        
        if group_value:
            # Buscamos otros productos con el mismo código de grupo, excluyendo al actual.
            # Filtramos solo productos 'Standalone' (parents/childs ya no se usan en tu lógica).
            siblings = Product.objects.filter(
                attribute_values__attribute__code=target_attr_code,
                attribute_values__value_text=group_value # Asumiendo que group_code es Texto
            ).exclude(id=product.id).distinct()
            
            ctx['siblings'] = siblings
        else:
            ctx['siblings'] = []

        return ctx