import os
import re
from oscar.apps.basket.abstract_models import AbstractLine


class Line(AbstractLine):
    """
    Custom Line model to format description with cleaner file paths
    """
    
    @property
    def description(self):
        """
        Override description to show cleaner file names in options.
        Instead of: (Sube tu Foto = 'uploads/Screenshot...')
        Shows: ('Screenshot...')
        """
        d = self.product.get_title()
        ops = []
        for attribute in self.attributes.all():
            value = attribute.value
            # If the value looks like a file path, extract just the filename
            if isinstance(value, str) and ('/' in value or '\\' in value):
                value = "'" + os.path.basename(value) + "'"
            ops.append(f"{value}")
        if ops:
            d = f"{d} ({', '.join(ops)})"
        return d


from oscar.apps.basket.models import *  # noqa: F401, E402
