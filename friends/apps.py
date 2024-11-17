from django.apps import AppConfig


class FriendsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'friends'
    
    # def ready(self):
    #     # Import and run table creation
    #     from .utils import create_dynamodb_tables
    #     create_dynamodb_tables()
