import os
import base64
import requests
from typing import Dict, Any
from app.config import settings

def analyze_wine_label(image_path: str) -> Dict[str, Any]:
    """
    Analyze a wine label image using OpenAI Vision API.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dict with analysis results including wine metadata
    """
    api_key = settings.openai_api_key
    
    if not api_key:
        return {
            "success": False,
            "error": "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        }
    
    try:
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a wine expert assistant. Extract detailed information from this wine label and return a comprehensive description."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Please analyze this wine label and provide information about the wine. Extract as much detail as possible including name, producer, vintage, type, varietal, region, and any other relevant information."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 800
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        description = result["choices"][0]["message"]["content"]
        
        # Extract key metadata from the description
        wine_metadata = extract_wine_metadata(description)
        
        return {
            "success": True,
            "description": description,
            "wine_metadata": wine_metadata
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def extract_wine_metadata(description: str) -> Dict[str, Any]:
    """
    Extract structured metadata from the wine description.
    This is a simple implementation - in production, you might want to use
    a more sophisticated approach or even another API call.
    
    Args:
        description: The wine description from OpenAI
        
    Returns:
        Dict with structured wine metadata
    """
    import re
    
    metadata = {
        "name": "",
        "producer": "",
        "vintage": None,
        "type": "",
        "varietal": "",
        "region": "",
        "country": ""
    }
    
    # Extract vintage (4-digit year)
    vintage_match = re.search(r'\b(19|20)\d{2}\b', description)
    if vintage_match:
        try:
            metadata["vintage"] = int(vintage_match.group(0))
        except ValueError:
            pass
    
    # Extract wine type
    type_patterns = [
        r'(?:Type|Wine Type|Style):\s*(Red|White|Rosé|Sparkling|Dessert)',
        r'(?:Type|Wine Type|Style):\s*([^,\n.]+)'
    ]
    
    for pattern in type_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            metadata["type"] = match.group(1).strip()
            break
    
    # Extract other fields - this is simplified and would be more robust in production
    for field in ["name", "producer", "varietal", "region", "country"]:
        patterns = [
            rf'(?:{field.title()}):\s*([^,\n.]+)',
            rf'(?:{field.title()}):\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                metadata[field] = match.group(1).strip()
                break
    
    return metadata