// label-scanner.js - Wine label scanning functionality

import api from './api.js';

/**
 * Functions for handling wine label scanning and analysis
 */
const labelScanner = {
    /**
     * Capture a photo from the device camera
     * @returns {Promise<File>} - Image file or null if canceled
     */
    capturePhoto: async () => {
        return new Promise((resolve) => {
            // Trigger the camera input
            const cameraInput = document.getElementById('camera-input');
            
            // Listen for file selection
            const handleChange = () => {
                if (cameraInput.files && cameraInput.files.length > 0) {
                    resolve(cameraInput.files[0]);
                } else {
                    resolve(null);
                }
                
                // Clean up event listener
                cameraInput.removeEventListener('change', handleChange);
            };
            
            cameraInput.addEventListener('change', handleChange);
            cameraInput.click();
        });
    },
    
    /**
     * Create a preview of the selected image
     * @param {File} imageFile - The image file
     * @returns {Promise<string>} - Data URL for the image preview
     */
    createImagePreview: async (imageFile) => {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.readAsDataURL(imageFile);
        });
    },
    
    /**
     * Analyze a wine label using the backend API
     * @param {File} imageFile - The wine label image
     * @returns {Promise<Object>} - Analysis results
     */
    analyzeLabel: async (imageFile) => {
        try {
            const results = await api.wines.analyzeLabel(imageFile);
            return results;
        } catch (error) {
            console.error('Error analyzing wine label:', error);
            throw error;
        }
    },
    
    /**
     * Extract wine data from analysis results
     * @param {Object} analysisResults - The analysis results from the API
     * @returns {Object} - Extracted wine data
     */
    extractWineData: (analysisResults) => {
        // Default empty wine data
        const wineData = {
            name: '',
            producer: '',
            vintage: '',
            type: '',
            region: '',
            country: '',
            description: ''
        };
        
        // If analysis was successful, extract the data
        if (analysisResults.success) {
            // Get wine details from the key_info
            if (analysisResults.key_info) {
                wineData.name = analysisResults.key_info.name || '';
                wineData.producer = analysisResults.key_info.producer || '';
                wineData.vintage = analysisResults.key_info.vintage || '';
                wineData.type = analysisResults.key_info.type || '';
                wineData.region = analysisResults.key_info.region || '';
                wineData.country = analysisResults.key_info.country || '';
            }
            
            // Store the full description
            wineData.description = analysisResults.description || '';
            
            // If there's a label image URL, store it
            if (analysisResults.label_image_url) {
                wineData.label_image_url = analysisResults.label_image_url;
            }
        }
        
        return wineData;
    }
};

export default labelScanner;