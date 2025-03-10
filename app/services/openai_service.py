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
        Returns a comprehensive description of the wine.
        """
        try:
            # Ensure image_path is a Path object
            if isinstance(image_path, str):
                image_path = Path(image_path)
            
            # Check if the file exists
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}"
                }
            
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a wine expert assistant. Extract information from this wine label and create a comprehensive description. Include the name, producer, vintage, region, country, varietal(s), and type (red, white, etc.) if present. Also include any relevant information about the wine's style and potential taste profile based on your expertise. Present this information in a well-formatted structure with clear headings."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Please analyze this wine label and provide a complete description."
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=800
            )
            
            description = response.choices[0].message.content
            
            # Extract clean description (plain text without markdown)
            clean_description = self._extract_clean_description(description)
            
            # Extract key fields for database filtering/searching
            key_info = self._extract_key_fields(description)
            
            return {
                "success": True,
                "description": description,
                "clean_description": clean_description,
                "key_info": key_info
            }
                
        except Exception as e:
            logger.error(f"Error analyzing wine label: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_clean_description(self, markdown_description: str) -> str:
        """Extract a clean, plain text description from the OpenAI markdown response."""
        # Look for a line containing "Description:" and extract the content after it
        import re
        desc_match = re.search(r'\*\*Description\*\*:?\s*(.*?)(?:\n|$)', markdown_description)
        if desc_match:
            return desc_match.group(1).strip()
        
        # Fallback: if no description line found, look for a substantial paragraph
        lines = markdown_description.split('\n')
        for line in lines:
            line = line.strip()
            # Find a line that's not a header and has substantial content
            if not line.startswith('*') and not line.startswith('-') and len(line) > 40:
                return line
        
        # Last resort
        return "Wine description from analysis"

    def _extract_key_fields(self, description: str) -> Dict[str, Any]:
        """
        Extract key fields from the description for database storage.
        This is a simple extraction for basic filtering/sorting purposes.
        """
        key_info = {
            "name": "",
            "producer": "",
            "vintage": None,
            "type": "",
            "region": "",
            "country": "",
            "varietal": []
        }
        
        # Simple extraction based on common patterns in the GPT response
        import re
        
        # Look for wine name - typically has specific patterns
        name_patterns = [
            r'(?:Name|Wine):\s*([^\n]+)',
            r'(?:Name|Wine):\*\*\s*([^\n]+)',
            r'\*\*(?:Name|Wine):\*\*\s*([^\n]+)'
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, description)
            if name_match:
                key_info["name"] = name_match.group(1).strip()
                break
                
        # Look for producer
        producer_patterns = [
            r'(?:Producer|Winery):\s*([^\n]+)',
            r'(?:Producer|Winery):\*\*\s*([^\n]+)',
            r'\*\*(?:Producer|Winery):\*\*\s*([^\n]+)'
        ]
        
        for pattern in producer_patterns:
            producer_match = re.search(pattern, description)
            if producer_match:
                key_info["producer"] = producer_match.group(1).strip()
                break
                
        # Look for vintage - extract 4-digit year
        vintage_match = re.search(r'\b(19|20)\d{2}\b', description)
        if vintage_match:
            try:
                key_info["vintage"] = int(vintage_match.group(0))
            except:
                pass
                
        # Look for wine type
        type_patterns = [
            r'(?:Type|Wine Type|Style):\s*(Red|White|Rosé|Rose|Sparkling|Dessert)',
            r'(?:Type|Wine Type|Style):\*\*\s*(Red|White|Rosé|Rose|Sparkling|Dessert)',
            r'\*\*(?:Type|Wine Type|Style):\*\*\s*(Red|White|Rosé|Rose|Sparkling|Dessert)'
        ]
        
        for pattern in type_patterns:
            type_match = re.search(pattern, description, re.IGNORECASE)
            if type_match:
                key_info["type"] = type_match.group(1).strip()
                break
        
        # If we don't have a type yet, look for general mentions of wine types
        if not key_info["type"]:
            general_type_match = re.search(r'\b(Red|White|Rosé|Rose|Sparkling|Dessert)\b(?:\s+wine)?', description, re.IGNORECASE)
            if general_type_match:
                key_info["type"] = general_type_match.group(1).strip()
        
        # Extract region and country using similar patterns
        region_patterns = [
            r'(?:Region):\s*([^\n]+)',
            r'(?:Region):\*\*\s*([^\n]+)',
            r'\*\*(?:Region):\*\*\s*([^\n]+)'
        ]
        
        for pattern in region_patterns:
            region_match = re.search(pattern, description)
            if region_match:
                key_info["region"] = region_match.group(1).strip()
                break
                
        country_patterns = [
            r'(?:Country):\s*([^\n]+)',
            r'(?:Country):\*\*\s*([^\n]+)',
            r'\*\*(?:Country):\*\*\s*([^\n]+)'
        ]
        
        for pattern in country_patterns:
            country_match = re.search(pattern, description)
            if country_match:
                key_info["country"] = country_match.group(1).strip()
                break
        
        # Extract varietal information
        varietal_patterns = [
            r'(?:Varietal|Varietals|Grape|Grapes):\s*([^\n]+)',
            r'(?:Varietal|Varietals|Grape|Grapes):\*\*\s*([^\n]+)',
            r'\*\*(?:Varietal|Varietals|Grape|Grapes):\*\*\s*([^\n]+)'
        ]
        
        for pattern in varietal_patterns:
            varietal_match = re.search(pattern, description, re.IGNORECASE)
            if varietal_match:
                # Try to split into a list if there are multiple varietals
                varietals_text = varietal_match.group(1).strip()
                # Split by common separators
                if ',' in varietals_text:
                    key_info["varietal"] = [v.strip() for v in varietals_text.split(',')]
                elif ' and ' in varietals_text.lower():
                    key_info["varietal"] = [v.strip() for v in varietals_text.split(' and ')]
                else:
                    key_info["varietal"] = [varietals_text]
                break
        
        return key_info
    
    def get_wine_pairing(self, food_description: str, available_wines: List[Wine]) -> Dict[str, Any]:
        """
        Get wine pairing recommendations based on food description and available wines.
        Uses wine descriptions for more informed recommendations.
        """
        try:
            # Format available wines with their descriptions
            wines_context = ""
            for i, wine in enumerate(available_wines, 1):
                wine_info = f"{i}. {wine.name}"
                if wine.vintage:
                    wine_info += f" ({wine.vintage})"
                if wine.producer:
                    wine_info += f" by {wine.producer}"
                if wine.type:
                    wine_info += f" - {wine.type} wine"
                if wine.wine_metadata and "description" in wine.wine_metadata:
                    wine_info += f"\n   {wine.wine_metadata['description']}"
                wines_context += wine_info + "\n\n"
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
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
            wines_context = ""
            for i, wine in enumerate(available_wines, 1):
                wine_info = f"{i}. {wine.name}"
                if wine.vintage:
                    wine_info += f" ({wine.vintage})"
                if wine.producer:
                    wine_info += f" by {wine.producer}"
                if wine.type:
                    wine_info += f" - {wine.type} wine"
                if wine.wine_metadata and "description" in wine.wine_metadata:
                    wine_info += f"\n   {wine.wine_metadata['description']}"
                wines_context += wine_info + "\n\n"
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
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