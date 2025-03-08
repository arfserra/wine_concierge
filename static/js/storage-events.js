// Add event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Fetch storage configurations
    fetchStorageConfigurations();
    
    // Add event listener for form submission
    document.getElementById('save-storage-btn').addEventListener('click', function(e) {
        e.preventDefault();
        const storageId = this.dataset.storageId;
        if (storageId) {
            updateStorageConfiguration(storageId);
        } else {
            saveStorageConfiguration();
        }
    });
    
    // Add listener for storage type changes
    document.getElementById('storage-type').addEventListener('change', function(e) {
        const alpineData = getAlpineData();
        if (alpineData) {
            alpineData.storageType = e.target.value;
        }
    });
    
    // Add listener for escape key to close modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
});

// View storage details
function viewStorage(id) {
    console.log("Viewing storage with ID:", id);
    
    try {
        // Show loading modal
        const loadingModal = `
            <div id="storage-modal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
                    <div class="px-6 py-4 border-b">
                        <div class="flex justify-between items-center">
                            <h3 class="text-xl font-semibold text-gray-900">Loading Storage Details...</h3>
                            <button onclick="closeModal()" class="text-gray-400 hover:text-gray-500">
                                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="px-6 py-12 flex justify-center items-center">
                        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-wine-700"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Add loading modal to body
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = loadingModal;
        document.body.appendChild(modalContainer);
        
        // Prevent scrolling on the body
        document.body.style.overflow = 'hidden';
        
        // Fetch storage details
        fetch(`/api/storage/${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to fetch storage details (Status: ${response.status})`);
                }
                return response.json();
            })
            .then(storage => {
                // Render storage details in modal
                const modalHTML = `
                    <div id="storage-modal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
                        <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
                            <div class="px-6 py-4 border-b">
                                <div class="flex justify-between items-center">
                                    <h3 class="text-xl font-semibold text-gray-900">${storage.name}</h3>
                                    <button onclick="closeModal()" class="text-gray-400 hover:text-gray-500">
                                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div class="px-6 py-4">
                                <div class="mb-4">
                                    <span class="inline-block px-2 py-1 bg-gray-200 rounded-full text-sm">${storage.type}</span>
                                    <p class="mt-2">Total positions: ${storage.total_positions}</p>
                                    <p>Naming scheme: ${storage.position_naming_scheme}</p>
                                </div>
                                
                                <!-- Display zones if present -->
                                ${renderStorageDetails(storage)}
                            </div>
                            <div class="px-6 py-3 border-t flex justify-end">
                                <button onclick="closeModal()" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">Close</button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Update modal content
                modalContainer.innerHTML = modalHTML;
            })
            .catch(error => {
                console.error('Error viewing storage:', error);
                
                // Show error in modal
                const errorModal = `
                    <div id="storage-modal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
                        <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full">
                            <div class="px-6 py-4 border-b">
                                <div class="flex justify-between items-center">
                                    <h3 class="text-xl font-semibold text-gray-900">Error</h3>
                                    <button onclick="closeModal()" class="text-gray-400 hover:text-gray-500">
                                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div class="px-6 py-4">
                                <div class="p-4 bg-red-50 border border-red-200 rounded-md">
                                    <p class="text-red-700">Failed to load storage details: ${error.message}</p>
                                </div>
                            </div>
                            <div class="px-6 py-3 border-t flex justify-end">
                                <button onclick="closeModal()" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">Close</button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Replace modal with error
                modalContainer.innerHTML = errorModal;
            });
    } catch (error) {
        console.error('Error viewing storage:', error);
        alert(`Error viewing storage: ${error.message}`);
    }
}

// Edit storage configuration
function editStorage(id) {
    console.log("Editing storage with ID:", id);
    
    try {
        // Fetch storage details
        fetch(`/api/storage/${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to fetch storage details (Status: ${response.status})`);
                }
                return response.json();
            })
            .then(storage => {
                // Get Alpine data
                const alpineData = getAlpineData();
                if (!alpineData) {
                    alert('Error accessing form data. Please try again.');
                    return;
                }
                
                // Fill in basic form fields
                document.getElementById('storage-name').value = storage.name || '';
                document.getElementById('storage-type').value = storage.type || 'Wine Rack';
                document.getElementById('naming-scheme').value = storage.position_naming_scheme || 'Section-Row-Column';
                
                // Check if we have multiple zones
                const hasMultipleZones = storage.zones && storage.zones.length > 1;
                
                // Update Alpine.js data
                alpineData.storageType = storage.type;
                alpineData.zoneEnabled = hasMultipleZones;
                
                // Set zones data
                if (storage.zones && storage.zones.length > 0) {
                    // Transform zones to match Alpine format
                    alpineData.zones = storage.zones.map(zone => {
                        const dims = zone.dimensions || {};
                        return {
                            name: zone.name || 'Zone',
                            rows: dims.rows || 1,
                            columns: dims.columns || 1,
                            temperature: zone.temperature || 55
                        };
                    });
                }
                
                // If we have a single zone, set standard dimensions
                if (!hasMultipleZones && storage.zones && storage.zones.length === 1) {
                    const zone = storage.zones[0];
                    const dims = zone.dimensions || {};
                    
                    if (storage.type === 'Wine Rack') {
                        alpineData.rows = dims.rows || 1;
                        alpineData.columns = dims.columns || 1;
                    } else if (storage.type === 'Wine Fridge') {
                        alpineData.sections = dims.sections || 1;
                        alpineData.shelves = dims.rows || 1;
                        alpineData.bottlesPerShelf = dims.columns || 1;
                    } else {
                        alpineData.sections = dims.sections || 1;
                        alpineData.rows = dims.rows || 1;
                        alpineData.columns = dims.columns || 1;
                    }
                }
                
                // Change form for updating
                const saveButton = document.getElementById('save-storage-btn');
                saveButton.textContent = 'Update Storage Configuration';
                saveButton.dataset.storageId = id;
                
                // Scroll to form
                const formContainer = document.querySelector('.mt-10.bg-white');
                if (formContainer) {
                    formContainer.scrollIntoView({ behavior: 'smooth' });
                }
            })
            .catch(error => {
                console.error('Error fetching storage details:', error);
                alert(`Failed to load storage details: ${error.message}`);
            });
    } catch (error) {
        console.error('Error editing storage:', error);
        alert(`Error editing storage: ${error.message}`);
    }
}

// Delete storage configuration
function deleteStorage(id) {
    if (confirm('Are you sure you want to delete this storage? This will also remove all wines stored in it.')) {
        try {
            fetch(`/api/storage/${id}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.detail || 'Failed to delete storage');
                    });
                }
                
                alert('Storage deleted successfully!');
                window.location.reload();
            })
            .catch(error => {
                console.error('Error deleting storage:', error);
                alert(`Failed to delete storage: ${error.message}`);
            });
        } catch (error) {
            console.error('Error deleting storage:', error);
            alert(`Failed to delete storage: ${error.message}`);
        }
    }
}

// Close modal function
function closeModal() {
    const modal = document.getElementById('storage-modal');
    if (modal) {
        modal.parentNode.removeChild(modal);
        document.body.style.overflow = '';
    }
}