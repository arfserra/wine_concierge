// storage-manager.js - Storage management functionality

import api from './api.js';

/**
 * Functions for managing wine storage configurations
 */
const storageManager = {
    /**
     * Generate all possible positions for a storage configuration
     * @param {Object} storage - Storage configuration object
     * @returns {Array<string>} - List of all possible positions
     */
    generatePositions: (storage) => {
        const positions = [];
        const scheme = storage.position_naming_scheme;
        
        if (storage.zones && storage.zones.length > 0) {
            // Generate positions for each zone
            storage.zones.forEach((zone) => {
                const dimensions = zone.dimensions || {};
                const rows = dimensions.rows || 1;
                const columns = dimensions.columns || 1;
                
                for (let r = 1; r <= rows; r++) {
                    for (let c = 1; c <= columns; c++) {
                        if (scheme === 'Sequential Numbering') {
                            // Simple number: 1, 2, 3, ...
                            const position = ((r - 1) * columns + c).toString();
                            positions.push(position);
                        } else if (scheme === 'Row-Column') {
                            // Format: 1A, 1B, 2A, ...
                            const position = `${r}${String.fromCharCode(64 + c)}`;
                            positions.push(position);
                        } else if (scheme === 'Zone-Position') {
                            // Format: Red Zone-A3, White Zone-B2, ...
                            const position = `${zone.name}-${r}${String.fromCharCode(64 + c)}`;
                            positions.push(position);
                        } else {
                            // Default format: Section-Row-Column
                            const position = `${zone.name}-${r}-${c}`;
                            positions.push(position);
                        }
                    }
                }
            });
        } else {
            // Fallback for simple storage with no zones
            for (let i = 1; i <= storage.total_positions; i++) {
                positions.push(`Position ${i}`);
            }
        }
        
        return positions;
    },
    
    /**
     * Get all available (not occupied) positions for a storage
     * @param {string} storageId - Storage ID
     * @returns {Promise<Array<string>>} - List of available positions
     */
    getAvailablePositions: async (storageId) => {
        try {
            // First get storage details
            const storage = await api.storage.getById(storageId);
            
            // Then get all wines
            const wines = await api.wines.getAll();
            
            // Get all positions in the storage
            const allPositions = storageManager.generatePositions(storage);
            
            // Find occupied positions in this storage
            const occupiedPositions = new Set(
                wines
                    .filter(wine => wine.storage_id === storageId)
                    .map(wine => wine.position)
            );
            
            // Return available positions (those not in occupiedPositions)
            return allPositions.filter(position => !occupiedPositions.has(position));
        } catch (error) {
            console.error('Error getting available positions:', error);
            return [];
        }
    },
    
    /**
     * Calculate total positions for a storage configuration
     * @param {Object} storage - Storage configuration object
     * @returns {number} - Total number of positions
     */
    calculateTotalPositions: (storage) => {
        let total = 0;
        
        if (storage.zones && storage.zones.length > 0) {
            storage.zones.forEach((zone) => {
                const dimensions = zone.dimensions || {};
                const rows = dimensions.rows || 1;
                const columns = dimensions.columns || 1;
                
                total += rows * columns;
            });
        }
        
        return total;
    },
    
    /**
     * Create a new storage configuration
     * @param {Object} storageData - Storage configuration data
     * @returns {Promise<Object>} - Created storage
     */
    createStorage: async (storageData) => {
        // Calculate total positions before saving
        storageData.total_positions = storageManager.calculateTotalPositions(storageData);
        
        return api.storage.create(storageData);
    },
    
    /**
     * Update an existing storage configuration
     * @param {string} storageId - Storage ID
     * @param {Object} storageData - Updated storage data
     * @returns {Promise<Object>} - Updated storage
     */
    updateStorage: async (storageId, storageData) => {
        // Calculate total positions before saving
        storageData.total_positions = storageManager.calculateTotalPositions(storageData);
        
        return api.storage.update(storageId, storageData);
    }
};

export default storageManager;