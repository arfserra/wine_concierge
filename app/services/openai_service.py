# app/services/openai_service.py
import os
import logging
import base64
from typing import List, Dict, Any, Optional, Union
import openai
from openai import OpenAI
from pathlib import Path

from app.config import settings
from app.models.wine import Wine

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.client = OpenAI(api_key=self.api_key)
        
    def analyze_wine_label(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze a wine label image using OpenAI's Vision capabilities.
        Returns extracted wine information.
        """
        try:
            # Ensure image_path is a Path object
            if isinstance(image_path, str):
                image_path = Path(image_path)
            
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="chatgpt-4o-latest",  # Updated to current model with vision capabilities
                messages=[
                    {
                        "role": "system",
                        "content": "You are a wine expert assistant. Extract all relevant information from this wine label image."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Please extract the following details from this wine label: name, producer, vintage, region, country, varietal(s), and type (red, white, etc.)."
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Process and structure the response
            extracted_info = self._parse_label_extraction(response.choices[0].message.content)
            return {
                "success": True,
                "data": extracted_info,
                "confidence_score": self._calculate_confidence_score(extracted_info),
                "raw_response": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error analyzing wine label: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_wine_pairing(self, food_description: str, available_wines: List[Wine]) -> Dict[str, Any]:
        """
        Get wine pairing recommendations based on food description and available wines.
        """
        try:
            # Format available wines for context
            wines_context = self._format_wines_for_context(available_wines)
            
            response = self.client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a wine pairing expert. Recommend wines exclusively from the user's available collection."
                    },
                    {
                        "role": "user",
                        "content": f"I'm planning to eat: {food_description}\n\nHere are the wines in my collection:\n{wines_context}\n\nWhat wine from my collection would pair best with this food? Provide your top recommendation with explanation."
                    }
                ],
                max_tokens=800
            )
            
            return {
                "success": True,
                "recommendation": response.choices[0].message.content,
                "food": food_description
            }
            
        except Exception as e:
            logger.error(f"Error getting wine pairing: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_food_image(self, image_path: Union[str, Path], available_wines: List[Wine]) -> Dict[str, Any]:
        """
        Analyze a food image and recommend wine pairings from available collection.
        """
        try:
            # Ensure image_path is a Path object
            if isinstance(image_path, str):
                image_path = Path(image_path)
                
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
            # Format available wines for context
            wines_context = self._format_wines_for_context(available_wines)
            
            response = self.client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a culinary and wine pairing expert. Identify the dish in the image and recommend appropriate wine pairings from the user's collection."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": f"What dish is shown in this image, and which wine from my collection would pair best with it?\n\nHere are the wines in my collection:\n{wines_context}"
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                max_tokens=800
            )
            
            return {
                "success": True,
                "recommendation": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error analyzing food image: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_wines_for_context(self, wines: List[Wine]) -> str:
        """Format wines list as a structured text for OpenAI context."""
        wines_text = ""
        for i, wine in enumerate(wines, 1):
            vintage_str = f", {wine.vintage}" if wine.vintage else ""
            region_str = f", {wine.region}" if wine.region else ""
            country_str = f", {wine.country}" if wine.country else ""
            varietal_str = f", {', '.join(wine.varietal)}" if wine.varietal else ""
            location_str = f" (Location: {wine.position})" if wine.position else ""
            
            wines_text += f"{i}. {wine.name} by {wine.producer}{vintage_str}{varietal_str}{region_str}{country_str}{location_str}\n"
        
        return wines_text
    
    def _parse_label_extraction(self, content: str) -> Dict[str, Any]:
        """Parse the text response from OpenAI into structured data."""
        # This is a simplified example - in production you'd want more robust parsing
        extracted = {
            "name": "",
            "producer": "",
            "vintage": None,
            "region": "",
            "country": "",
            "varietal": [],
            "type": ""
        }
        
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == "name" or key == "wine name":
                    extracted["name"] = value
                elif key == "producer" or key == "winery":
                    extracted["producer"] = value
                elif key == "vintage" or key == "year":
                    try:
                        extracted["vintage"] = int(value)
                    except:
                        # Try to extract just the year if there's other text
                        import re
                        year_match = re.search(r'\b(19|20)\d{2}\b', value)
                        if year_match:
                            extracted["vintage"] = int(year_match.group(0))
                elif key == "region":
                    extracted["region"] = value
                elif key == "country":
                    extracted["country"] = value
                elif key == "varietal" or key == "grape" or key == "varietals" or key == "grapes":
                    # Handle multiple varietals separated by commas or 'and'
                    varietals = [v.strip() for v in value.replace(' and ', ',').split(',')]
                    extracted["varietal"] = varietals
                elif key == "type" or key == "wine type":
                    extracted["type"] = value
        
        return extracted
    
    def _calculate_confidence_score(self, extracted_info: Dict[str, Any]) -> float:
        """
        Calculate a confidence score based on completeness of extracted information.
        """
        # Simple scoring based on field presence
        required_fields = ["name", "producer"]
        optional_fields = ["vintage", "varietal", "type", "region", "country"]
        
        score = 0.0
        total_weight = len(required_fields) + 0.5 * len(optional_fields)
        
        for field in required_fields:
            if extracted_info.get(field):
                score += 1.0
                
        for field in optional_fields:
            if extracted_info.get(field):
                score += 0.5
                
        return min(score / total_weight, 1.0)