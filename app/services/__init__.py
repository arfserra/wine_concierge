# Don't try to import the analyze_wine_label function directly
# Just import the module itself
from app.services import storage_service

__all__ = ["storage_service"]