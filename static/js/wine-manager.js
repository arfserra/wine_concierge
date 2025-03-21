// wine-manager.js - Wine collection management functionality

import api from './api.js';

/**
 * Functions for managing the wine collection
 */
const wineManager = {
    /**
     * Filter wines based on search and filter criteria
     * @param {Array} wines - List of all wines
     * @param {Object} filters - Filter criteria
     * @returns {Array} - Filtered wines
     */
    filterWines: (wines, filters) => {
        return wines.filter(wine => {
            // Text search
            if (filters.search) {
                const searchTerm = filters.search.toLowerCase();
                const matches = 
                    (wine.name && wine.name.toLowerCase().includes(searchTerm)) ||
                    (wine.producer && wine.producer.toLowerCase().includes(searchTerm)) ||
                    (wine.region && wine.region.toLowerCase().includes(searchTerm)) ||
                    (wine.country && wine.country.toLowerCase().includes(searchTerm)) ||
                    (wine.vintage && wine.vintage.toString().includes(searchTerm));
                
                if (!matches) return false;
            }
            
            // Type filter
            if (filters.type && wine.type !== filters.type) {
                return false;
            }
            
            // Country filter
            if (filters.country && wine.country !== filters.country) {
                return false;
            }
            
            // Storage filter
            if (filters.storage && wine.storage_id !== filters.storage) {
                return false;
            }
            
            return true;
        });
    },
    
    /**
     * Extract filter options from wines for display
     * @param {Array} wines - List of wines
     * @returns {Object} - Filter options
     */
    extractFilterOptions: (wines) => {
        const options = {
            countries: [],
            regions: [],
            types: ['Red', 'White', 'Rosé', 'Sparkling', 'Dessert'],
        };
        
        // Extract unique values
        const countries = new Set();
        const regions = new Set();
        
        wines.forEach(wine => {
            if (wine.country) countries.add(wine.country);
            if (wine.region) regions.add(wine.region);
        });
        
        // Convert to sorted arrays
        options.countries = [...countries].sort();
        options.regions = [...regions].sort();
        
        return options;
    },
    
    /**
     * Sort wines by different criteria
     * @param {Array} wines - List of wines
     * @param {string} sortBy - Sort criterion ('name', 'date', 'vintage')
     * @param {boolean} ascending - Sort direction
     * @returns {Array} - Sorted wines
     */
    sortWines: (wines, sortBy = 'date', ascending = false) => {
        const sortedWines = [...wines];
        
        sortedWines.sort((a, b) => {
            let valueA, valueB;
            
            if (sortBy === 'date') {
                valueA = new Date(a.added_date).getTime();
                valueB = new Date(b.added_date).getTime();
            } else if (sortBy === 'vintage') {
                valueA = a.vintage || 0;
                valueB = b.vintage || 0;
            } else {
                // Default to sorting by name
                valueA = a.name || '';
                valueB = b.name || '';
            }
            
            if (valueA < valueB) return ascending ? -1 : 1;
            if (valueA > valueB) return ascending ? 1 : -1;
            return 0;
        });
        
        return sortedWines;
    },
    
    /**
     * Match storage names to wines
     * @param {Array} wines - List of wines
     * @param {Array} storages - List of storage configurations
     * @returns {Array} - Wines with storage_name property added
     */
    matchStorageNames: (wines, storages) => {
        const storageMap = {};
        
        // Create a map of storage IDs to names
        storages.forEach(storage => {
            storageMap[storage.id] = storage.name;
        });
        
        // Add storage_name to each wine
        return wines.map(wine => ({
            ...wine,
            storage_name: storageMap[wine.storage_id] || 'Unknown Storage'
        }));
    },
    
    /**
     * Add a new wine to the collection
     * @param {Object} wineData - Wine data
     * @param {File} labelImage - Optional wine label image
     * @returns {Promise<Object>} - Created wine
     */
    addWine: async (wineData, labelImage = null) => {
        return api.wines.add(wineData, labelImage);
    }
};

export default wineManager;