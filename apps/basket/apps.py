import oscar.apps.basket.apps as apps


class BasketConfig(apps.BasketConfig):
    name = 'apps.basket'
    label = 'basket'
    verbose_name = 'Cesta'
