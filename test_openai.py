import asyncio
from pathlib import Path
from app.services.openai_service import OpenAIService

async def test_openai():
    service = OpenAIService()
    
    # Replace with the path to a sample wine label image you have available
    test_image_path = Path("20685.jpg")
    
    if not test_image_path.exists():
        print(f"Test image not found at {test_image_path}")
        return
    
    print(f"Analyzing wine label at {test_image_path}...")
    result = service.analyze_wine_label(test_image_path)
    
    if result["success"]:
        print("Analysis successful!")
        print(f"Confidence score: {result['confidence_score']}")
        print("\nExtracted information:")
        for key, value in result["data"].items():
            print(f"  {key}: {value}")
        
        print("\nRaw response:")
        print(result["raw_response"])
    else:
        print(f"Analysis failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_openai())