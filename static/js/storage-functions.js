// Helper function to get Alpine.js data
// Helper function to get Alpine.js data
function getAlpineData() {
    try {
        // Look for the form container with Alpine data
        const alpineElement = document.querySelector('.space-y-6[x-data]');
        
        if (!alpineElement) {
            console.error("Couldn't find Alpine element");
            return null;
        }
        
        // Alpine 3.x with $data
        if (alpineElement.__x && alpineElement.__x.$data) {
            return alpineElement.__x.$data;
        }
        
        // Alpine 3.x with reactive proxy
        if (alpineElement._x_dataStack && alpineElement._x_dataStack[0]) {
            return alpineElement._x_dataStack[0];
        }
        
        // Try to find __alpine API (newer versions)
        if (window.Alpine && alpineElement.__alpine) {
            return alpineElement.__alpine.getUnobservedData();
        }
        
        // Direct access to element's properties as a fallback
        if (alpineElement.zoneEnabled !== undefined) {
            return alpineElement;
        }
        
        console.error("Couldn't access Alpine.js data using known methods");
        return null;
    } catch (e) {
        console.error("Error accessing Alpine.js data:", e);
        return null;
    }
}

// Fetch all storage configurations
async function fetchStorageConfigurations() {
    try {
        const response = await fetch('/api/storage');
        const data = await response.json();
        
        const storageListElement = document.getElementById('storage-list');
        
        // Clear loading placeholder
        storageListElement.innerHTML = '';
        
        if (Array.isArray(data) && data.length > 0) {
            // Display each storage configuration
            data.forEach(storage => {
                // Check if storage has zones
                const hasZones = storage.zones && storage.zones.length > 0;
                const zoneInfo = hasZones ? 
                    `<p class="text-sm text-gray-600 mt-1">${storage.zones.length} zone${storage.zones.length > 1 ? 's' : ''}</p>` : '';
                
                storageListElement.innerHTML += `
                    <div class="bg-white rounded-lg shadow-md p-6">
                        <div class="flex justify-between items-center">
                            <h3 class="font-bold text-lg">${storage.name}</h3>
                            <span class="px-2 py-1 bg-gray-200 rounded-full text-sm">${storage.type}</span>
                        </div>
                        <div class="mt-2 text-sm text-gray-700">
                            <p>Total positions: ${storage.total_positions}</p>
                            <p>Naming scheme: ${storage.position_naming_scheme}</p>
                            ${zoneInfo}
                        </div>
                        <div class="mt-4 flex justify-end space-x-2">
                            <button onclick="viewStorage('${storage.id}')" class="px-3 py-1 bg-wine-500 text-white rounded hover:bg-wine-600 text-sm">View</button>
                            <button onclick="editStorage('${storage.id}')" class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm">Edit</button>
                            <button onclick="deleteStorage('${storage.id}')" class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm">Delete</button>
                        </div>
                    </div>
                `;
            });
        } else {
            // No storage configurations found
            storageListElement.innerHTML = `
                <div class="col-span-full p-6 bg-gray-50 rounded-lg border border-dashed border-gray-300 text-center">
                    <p class="text-gray-500">No storage configurations found. Create your first one below!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching storage configurations:', error);
        document.getElementById('storage-list').innerHTML = `
            <div class="col-span-full p-6 bg-red-50 rounded-lg border border-red-200 text-center">
                <p class="text-red-500">Failed to load storage configurations. Please try again.</p>
            </div>
        `;
    }
}

// Save new storage configuration
// Replace your saveStorageConfiguration function with this version
function saveStorageConfiguration() {
    console.log("Save function called");
    
    try {
        // Get basic form data
        const storageName = document.getElementById('storage-name').value;
        if (!storageName) {
            alert('Please enter a storage name');
            return;
        }
        
        const storageType = document.getElementById('storage-type').value;
        const namingScheme = document.getElementById('naming-scheme').value;
        
        // Check if custom zones are enabled directly from the checkbox
        const zoneEnabled = document.getElementById('zone-enabled').checked;
        console.log("Zone enabled (from checkbox):", zoneEnabled);
        
        // Prepare zones data based on enabled status
        let zones = [];
        
        if (zoneEnabled) {
            // Directly collect zones from DOM inputs
            zones = collectZonesDirectly();
            console.log("Collected zones from DOM:", zones);
        } else {
            // Create a single default zone based on standard dimensions
            if (storageType === 'Wine Rack') {
                const rows = parseInt(document.getElementById('rows')?.value) || 1;
                const columns = parseInt(document.getElementById('columns')?.value) || 1;
                
                zones = [
                    {
                        name: "Default Zone",
                        dimensions: {
                            rows: rows,
                            columns: columns
                        }
                    }
                ];
            } else if (storageType === 'Wine Fridge') {
                const sections = parseInt(document.getElementById('sections')?.value) || 1;
                const shelves = parseInt(document.getElementById('shelves')?.value) || 1;
                const bottlesPerShelf = parseInt(document.getElementById('bottles-per-shelf')?.value) || 1;
                
                zones = [
                    {
                        name: "Default Zone",
                        dimensions: {
                            rows: shelves,
                            columns: bottlesPerShelf,
                            sections: sections
                        }
                    }
                ];
            } else {
                const sections = parseInt(document.getElementById('other-sections')?.value) || 1;
                const rows = parseInt(document.getElementById('other-rows')?.value) || 1;
                const columns = parseInt(document.getElementById('other-columns')?.value) || 1;
                
                zones = [
                    {
                        name: "Default Zone",
                        dimensions: {
                            rows: rows,
                            columns: columns,
                            sections: sections
                        }
                    }
                ];
            }
            console.log("Created standard zone:", zones);
        }
        
        // Create storage data object
        const storageData = {
            name: storageName,
            type: storageType,
            zones: zones,
            position_naming_scheme: namingScheme
        };
        
        console.log("Sending storage data:", JSON.stringify(storageData, null, 2));
        
        // Make the API call
        fetch('/api/storage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(storageData)
        })
        .then(response => {
            console.log("API response status:", response.status);
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Failed to create storage');
                });
            }
            
            return response.json();
        })
        .then(data => {
            console.log("Success response:", data);
            alert('Storage configuration saved successfully!');
            
            // Reload the page
            window.location.reload();
        })
        .catch(error => {
            console.error("Error saving storage:", error);
            alert(`Failed to save storage: ${error.message}`);
        });
    } catch (error) {
        console.error('Error in saveStorageConfiguration:', error);
        alert('Error: ' + error.message);
    }
}

// Helper function to collect zones directly from the DOM
function collectZonesDirectly() {
    const zones = [];
    
    // Find all zone containers
    const zoneContainers = document.querySelectorAll('.p-4.border.border-gray-200.rounded-md.mb-4');
    console.log("Found zone containers:", zoneContainers.length);
    
    if (zoneContainers.length === 0) {
        // Fallback - return default zone
        return [{
            name: "Default Zone",
            dimensions: {
                rows: 4,
                columns: 6
            },
            temperature: 55
        }];
    }
    
    // For each container, find the inputs
    zoneContainers.forEach((container, index) => {
        // Find inputs within the container
        const nameInput = container.querySelector('input[id^="zone-name-"]');
        const rowsInput = container.querySelector('input[id^="zone-rows-"]');
        const columnsInput = container.querySelector('input[id^="zone-columns-"]');
        const tempInput = container.querySelector('input[id^="zone-temp-"]');
        
        // Get values with fallbacks
        const name = nameInput?.value || `Zone ${index + 1}`;
        const rows = parseInt(rowsInput?.value) || 1;
        const columns = parseInt(columnsInput?.value) || 1;
        const temperature = parseInt(tempInput?.value) || 55;
        
        // Add to zones array
        zones.push({
            name: name,
            dimensions: {
                rows: rows,
                columns: columns
            },
            temperature: temperature
        });
    });
    
    return zones;
}

// Update storage configuration
function updateStorageConfiguration(id) {
    console.log("Updating storage with ID:", id);
    
    try {
        // Get basic form data
        const storageName = document.getElementById('storage-name').value;
        if (!storageName) {
            alert('Please enter a storage name');
            return;
        }
        
        // Get Alpine.js data
        const alpineData = getAlpineData();
        if (!alpineData) {
            alert('Error accessing form data. Please try again.');
            return;
        }
        
        const storageType = document.getElementById('storage-type').value;
        const namingScheme = document.getElementById('naming-scheme').value;
        
        // Prepare zones data using the same approach as in saveStorageConfiguration
        let zones = [];
        
        if (alpineData.zoneEnabled) {
            zones = alpineData.zones.map(zone => ({
                name: zone.name,
                dimensions: {
                    rows: parseInt(zone.rows) || 1,
                    columns: parseInt(zone.columns) || 1
                },
                temperature: parseInt(zone.temperature) || 55
            }));
        } else {
            // Create a single zone based on standard dimensions
            if (storageType === 'Wine Rack') {
                zones = [
                    {
                        name: "Default Zone",
                        dimensions: {
                            rows: parseInt(alpineData.rows) || 1,
                            columns: parseInt(alpineData.columns) || 1
                        }
                    }
                ];
            } else if (storageType === 'Wine Fridge') {
                zones = [
                    {
                        name: "Default Zone",
                        dimensions: {
                            rows: parseInt(alpineData.shelves) || 1,
                            columns: parseInt(alpineData.bottlesPerShelf) || 1,
                            sections: parseInt(alpineData.sections) || 1
                        }
                    }
                ];
            } else {
                zones = [
                    {
                        name: "Default Zone",
                        dimensions: {
                            rows: parseInt(alpineData.rows) || 1,
                            columns: parseInt(alpineData.columns) || 1,
                            sections: parseInt(alpineData.sections) || 1
                        }
                    }
                ];
            }
        }
        
        // Create storage data object
        const storageData = {
            name: storageName,
            type: storageType,
            zones: zones,
            position_naming_scheme: namingScheme
        };
        
        // Make the API call
        fetch(`/api/storage/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(storageData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Failed to update storage');
                });
            }
            
            return response.json();
        })
        .then(data => {
            alert('Storage configuration updated successfully!');
            
            // Reset form and event handler
            document.getElementById('storage-form').reset();
            
            // Reset button state
            const saveButton = document.getElementById('save-storage-btn');
            saveButton.textContent = 'Save Storage Configuration';
            delete saveButton.dataset.storageId;
            
            // Reload the page
            window.location.reload();
        })
        .catch(error => {
            console.error('Error updating storage:', error);
            alert(`Failed to update storage: ${error.message}`);
        });
    } catch (error) {
        console.error('Error updating storage:', error);
        alert(`Error updating storage: ${error.message}`);
    }
}

// Helper function to render storage zones
function renderStorageDetails(storage) {
    // Check if storage has zones and it's a valid array
    const hasZones = storage.zones && Array.isArray(storage.zones) && storage.zones.length > 0;
    
    if (hasZones) {
        let zonesHTML = `
            <div class="mt-4">
                <h4 class="font-medium text-lg mb-2">Zones</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        `;
        
        storage.zones.forEach((zone, index) => {
            // Safely access zone properties
            const zoneName = zone.name || `Zone ${index + 1}`;
            const dimensions = zone.dimensions || {};
            const rows = dimensions.rows || 0;
            const columns = dimensions.columns || 0;
            const sections = dimensions.sections || 1;
            const capacity = rows * columns * sections;
            
            // Temperature info
            const temperatureInfo = zone.temperature ? 
                `<p class="text-sm">Temperature: ${zone.temperature}°F</p>` : '';
            
            zonesHTML += `
                <div class="border border-gray-200 rounded-md p-3">
                    <h5 class="font-medium">${zoneName}</h5>
                    <p class="text-sm">Dimensions: ${rows} rows × ${columns} columns${sections > 1 ? ` × ${sections} sections` : ''}</p>
                    <p class="text-sm">Capacity: ${capacity} bottles</p>
                    ${temperatureInfo}
                </div>
            `;
        });
        
        zonesHTML += `
                </div>
            </div>
        `;
        
        return zonesHTML;
    } else {
        return `
            <div class="mt-4 p-4 bg-gray-50 rounded-md border border-gray-200">
                <p class="text-gray-700">No zone information available for this storage.</p>
            </div>
        `;
    }
}