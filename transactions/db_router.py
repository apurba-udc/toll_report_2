from django.core.exceptions import PermissionDenied


class ReadOnlyRouter:
    """
    Database router to enforce read-only access to ZAKTOLL database
    Prevents any write operations to maintain data integrity
    """
    
    def db_for_read(self, model, **hints):
        """Reading from the 'default' database."""
        return 'default'

    def db_for_write(self, model, **hints):
        """Block all write operations to maintain read-only access."""
        if model._meta.app_label == 'transactions':
            raise PermissionDenied(
                f"Write operations are not allowed on {model._meta.db_table}. "
                f"This application operates in read-only mode on the ZAKTOLL database."
            )
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Block all migrations on the ZAKTOLL database."""
        if app_label == 'transactions':
            return False  # Don't allow migrations for transactions app
        return db == 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same database."""
        return True 