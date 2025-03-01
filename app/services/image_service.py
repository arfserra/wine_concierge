# app/services/image_service.py
import os
import uuid
from typing import Optional
from pathlib import Path
from fastapi import UploadFile
import shutil

from app.config import settings

class ImageService:
    def __init__(self, upload_dir: Optional[str] = None):
        self.upload_dir = upload_dir or settings.upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Create subdirectories for different image types
        self.wine_labels_dir = os.path.join(self.upload_dir, "wine_labels")
        self.food_images_dir = os.path.join(self.upload_dir, "food_images")
        
        os.makedirs(self.wine_labels_dir, exist_ok=True)
        os.makedirs(self.food_images_dir, exist_ok=True)
    
    async def save_wine_label(self, file: UploadFile) -> str:
        """
        Save a wine label image and return the path.
        """
        return await self._save_file(file, self.wine_labels_dir)
    
    async def save_food_image(self, file: UploadFile) -> str:
        """
        Save a food image and return the path.
        """
        return await self._save_file(file, self.food_images_dir)
    
    async def _save_file(self, file: UploadFile, directory: str) -> str:
        """
        Save an uploaded file to the specified directory.
        Returns the path to the saved file.
        """
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create the full save path
        save_path = os.path.join(directory, unique_filename)
        
        # Save the file
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return the relative path for storage in the database
        return os.path.relpath(save_path, start=settings.upload_dir)