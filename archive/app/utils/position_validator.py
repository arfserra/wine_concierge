from typing import Dict, Optional
from app.models.storage import Storage

class PositionValidator:
    """Utility class for validating wine positions within a storage unit."""
    
    @staticmethod
    def validate_position(position: str, storage: Storage) -> bool:
        """
        Validate that a position string is valid for the given storage.
        
        Args:
            position (str): Position string (e.g., "Red Zone-A3")
            storage (Storage): The storage configuration
            
        Returns:
            bool: True if the position is valid, False otherwise
        """
        # Empty position is considered valid (wine has no specific position)
        if not position:
            return True
            
        # Split zone and position parts
        parts = position.split('-')
        if len(parts) != 2:
            return False
            
        zone_name, position_code = parts
        
        # Find the matching zone
        matching_zone = None
        for zone in storage.zones:
            if zone.get('name') == zone_name:
                matching_zone = zone
                break
        
        if not matching_zone:
            return False
            
        # Parse the position according to the naming scheme
        dimensions = matching_zone.get('dimensions', {})
        
        if storage.position_naming_scheme == 'row-column':
            # Expect position like "A3" where A is row and 3 is column
            if len(position_code) < 2:
                return False
                
            row = position_code[0].upper()
            try:
                column = int(position_code[1:])
            except ValueError:
                return False
                
            # Convert row letter to number (A=1, B=2, etc.)
            row_num = ord(row) - ord('A') + 1
            
            # Check if within range
            if row_num < 1 or row_num > dimensions.get('rows', 0):
                return False
                
            if column < 1 or column > dimensions.get('columns', 0):
                return False
                
            return True
            
        elif storage.position_naming_scheme == 'numeric':
            # Expect position like "12" representing a numbered position
            try:
                position_num = int(position_code)
            except ValueError:
                return False
                
            # Calculate total positions in the zone
            total_zone_positions = 1
            for dimension_value in dimensions.values():
                total_zone_positions *= dimension_value
                
            # Check if within range
            if position_num < 1 or position_num > total_zone_positions:
                return False
                
            return True
            
        # Add additional naming schemes as needed
        return False
    
    @staticmethod
    def is_position_occupied(position: str, storage_id: str, db, wine_id: Optional[str] = None) -> bool:
        """
        Check if a position is already occupied by another wine.
        
        Args:
            position (str): Position string
            storage_id (str): Storage ID
            db: Database session
            wine_id (str, optional): Wine ID to exclude from check (for updates)
            
        Returns:
            bool: True if occupied, False otherwise
        """
        from app.models.wine import Wine
        
        # Empty position is never considered occupied
        if not position:
            return False
            
        query = db.query(Wine).filter(
            Wine.storage_id == storage_id,
            Wine.position == position
        )
        
        # If wine_id is provided, exclude it from the check (for updating wines)
        if wine_id:
            query = query.filter(Wine.id != wine_id)
            
        return query.first() is not None