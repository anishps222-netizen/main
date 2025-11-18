from django.apps import AppConfig

class FreelanceMarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'freelance_marketplace'

    def ready(self):
        import freelance_marketplace.signals