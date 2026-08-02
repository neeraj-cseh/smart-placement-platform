from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import os
        # Ensure it only runs once and not during migrations
        if os.environ.get('RUN_MAIN', None) == 'true':
            try:
                from core.scheduler import start_scheduler
                start_scheduler()
            except ImportError:
                pass
