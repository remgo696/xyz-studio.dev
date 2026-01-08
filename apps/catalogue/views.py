from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')

class ProductDetailView(CoreProductDetailView):
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        current_product = self.object
        
        # Buscamos hermanos con igual nombre e igual group_code
        group_code_attr = current_product.attribute_values.filter(attribute__code='group_code').first()
        
        if group_code_attr and group_code_attr.value:
            # Filtrar por nombre igual y group_code igual
            siblings = Product.objects.filter(
                title=current_product.title,
                attribute_values__attribute__code='group_code',
                attribute_values__value_text=group_code_attr.value
            ).exclude(id=current_product.id).distinct()
            
            ctx['color_siblings'] = siblings
        else:
            ctx['color_siblings'] = []
            
        return ctx