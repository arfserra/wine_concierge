// api.js - Core API integration for Wine Concierge

/**
 * Base API functions for interacting with the Wine Concierge backend
 */
const api = {
    /**
     * Base API URL - update this if your backend URL changes
     */
    baseUrl: '/api',
    
    /**
     * Generic fetch wrapper with error handling
     * @param {string} endpoint - API endpoint to call
     * @param {Object} options - Fetch options
     * @returns {Promise} - Response data
     */
    async fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `API Error: ${response.status}`);
            }
            
            // For DELETE requests, return success status
            if (options.method === 'DELETE') {
                return { success: true };
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    },
    
    /**
     * Wine-related API endpoints
     */
    wines: {
        /**
         * Get all wines in the collection
         * @param {string} storageId - Optional storage ID to filter by
         * @returns {Promise<Array>} - List of wines
         */
        getAll: async (storageId = null) => {
            const queryParams = storageId ? `?storage_id=${storageId}` : '';
            return api.fetch(`/wines${queryParams}`);
        },
        
        /**
         * Get a specific wine by ID
         * @param {string} wineId - Wine ID
         * @returns {Promise<Object>} - Wine details
         */
        getById: async (wineId) => {
            return api.fetch(`/wines/${wineId}`);
        },
        
        /**
         * Add a new wine to the collection
         * @param {Object} wineData - Wine data object
         * @param {File} labelImage - Optional wine label image file
         * @returns {Promise<Object>} - Created wine object
         */
        add: async (wineData, labelImage = null) => {
            const formData = new FormData();
            
            // Add wine data as JSON
            formData.append('wine_data', JSON.stringify(wineData));
            
            // Add label image if provided
            if (labelImage) {
                formData.append('label_image', labelImage);
            }
            
            return api.fetch('/wines', {
                method: 'POST',
                body: formData,
                // Don't set Content-Type header for FormData
                headers: {}
            });
        },
        
        /**
         * Update an existing wine
         * @param {string} wineId - Wine ID
         * @param {Object} wineData - Updated wine data
         * @returns {Promise<Object>} - Updated wine object
         */
        update: async (wineId, wineData) => {
            return api.fetch(`/wines/${wineId}`, {
                method: 'PUT',
                body: JSON.stringify(wineData)
            });
        },
        
        /**
         * Delete a wine from the collection
         * @param {string} wineId - Wine ID
         * @returns {Promise<Object>} - Success indicator
         */
        delete: async (wineId) => {
            return api.fetch(`/wines/${wineId}`, {
                method: 'DELETE'
            });
        },
        
        /**
         * Analyze a wine label image
         * @param {File} labelImage - Wine label image file
         * @returns {Promise<Object>} - Analysis results
         */
        analyzeLabel: async (labelImage) => {
            const formData = new FormData();
            formData.append('label_image', labelImage);
            
            return api.fetch('/wines/analyze', {
                method: 'POST',
                body: formData,
                headers: {}
            });
        }
    },
    
    /**
     * Storage-related API endpoints
     */
    storage: {
        /**
         * Get all storage configurations
         * @returns {Promise<Array>} - List of storage configurations
         */
        getAll: async () => {
            return api.fetch('/storage');
        },
        
        /**
         * Get a specific storage configuration
         * @param {string} storageId - Storage ID
         * @returns {Promise<Object>} - Storage configuration details
         */
        getById: async (storageId) => {
            return api.fetch(`/storage/${storageId}`);
        },
        
        /**
         * Create a new storage configuration
         * @param {Object} storageData - Storage configuration data
         * @returns {Promise<Object>} - Created storage configuration
         */
        create: async (storageData) => {
            return api.fetch('/storage', {
                method: 'POST',
                body: JSON.stringify(storageData)
            });
        },
        
        /**
         * Update an existing storage configuration
         * @param {string} storageId - Storage ID
         * @param {Object} storageData - Updated storage data
         * @returns {Promise<Object>} - Updated storage configuration
         */
        update: async (storageId, storageData) => {
            return api.fetch(`/storage/${storageId}`, {
                method: 'PUT',
                body: JSON.stringify(storageData)
            });
        },
        
        /**
         * Delete a storage configuration
         * @param {string} storageId - Storage ID
         * @returns {Promise<Object>} - Success indicator
         */
        delete: async (storageId) => {
            return api.fetch(`/storage/${storageId}`, {
                method: 'DELETE'
            });
        }
    }
};

// Export the API for use in other files
export default api;