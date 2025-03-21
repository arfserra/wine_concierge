# app/services/__init__.py
from app.services.openai_service import OpenAIService
from app.services.image_service import ImageService

# Create instances that can be imported from other parts of the app
openai_service = OpenAIService()
image_service = ImageService()

__all__ = ["OpenAIService", "ImageService", "openai_service", "image_service"]