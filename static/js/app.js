class MGNREGAApp {
    constructor() {
        this.currentDistrict = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupServiceWorker();
        this.loadCachedData();
    }

    setupEventListeners() {
        // District form submission
        const districtForm = document.getElementById('districtForm');
        if (districtForm) {
            districtForm.addEventListener('submit', (e) => this.handleFormSubmission(e));
        }

        // Location detection
        const detectBtn = document.getElementById('detectLocation');
        if (detectBtn) {
            detectBtn.addEventListener('click', () => this.detectUserLocation());
        }

        // Input validation
        this.setupInputValidation();
    }

    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }

    async detectUserLocation() {
        const detectBtn = document.getElementById('detectLocation');
        const resultDiv = document.getElementById('locationResult');
        
        if (!detectBtn || !resultDiv) return;

        // Show loading state
        detectBtn.disabled = true;
        detectBtn.innerHTML = '<div class="loading me-2"></div> Detecting...';

        try {
            // Try browser geolocation first
            if (navigator.geolocation) {
                const position = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject, {
                        timeout: 10000,
                        enableHighAccuracy: false,
                        maximumAge: 300000 // 5 minutes
                    });
                });

                const district = await this.getDistrictFromCoordinates(
                    position.coords.latitude,
                    position.coords.longitude
                );

                if (district) {
                    this.selectDistrict(district.code, district.name, district.name_hindi);
                    this.showLocationResult(`Detected: ${district.name} (${district.name_hindi})`, 'success');
                    return;
                }
            }

            // Fallback to IP-based detection
            await this.detectLocationByIP();

        } catch (error) {
            console.error('Location detection failed:', error);
            await this.detectLocationByIP();
        } finally {
            // Reset button state
            detectBtn.disabled = false;
            detectBtn.innerHTML = '<i class="fas fa-location-arrow me-2"></i> Auto Detect My District';
        }
    }

    async detectLocationByIP() {
        try {
            const response = await fetch('/api/detect-location');
            const data = await response.json();

            if (data.success) {
                this.selectDistrict(data.district_code, data.district_name, data.district_name_hindi);
                this.showLocationResult(
                    `Detected: ${data.district_name} (${data.district_name_hindi}) via ${data.method}`,
                    'info'
                );
            } else {
                this.showLocationResult('Could not detect location automatically. Please select manually.', 'warning');
            }
        } catch (error) {
            console.error('IP detection failed:', error);
            this.showLocationResult('Location detection failed. Please select district manually.', 'danger');
        }
    }

    async getDistrictFromCoordinates(lat, lon) {
        try {
            const response = await fetch(`/api/geolocation?lat=${lat}&lon=${lon}`);
            const data = await response.json();

            if (data.success) {
                return {
                    code: data.district_code,
                    name: data.district_name,
                    name_hindi: data.district_name_hindi
                };
            }
        } catch (error) {
            console.error('Coordinate detection failed:', error);
        }
        return null;
    }

    selectDistrict(code, name, name_hindi) {
        const districtSelect = document.getElementById('district');
        if (districtSelect) {
            districtSelect.value = code;
            this.currentDistrict = { code, name, name_hindi };
            
            // Trigger change event
            districtSelect.dispatchEvent(new Event('change'));
        }
    }

    showLocationResult(message, type) {
        const resultDiv = document.getElementById('locationResult');
        if (resultDiv) {
            resultDiv.className = `alert alert-${type} text-center`;
            resultDiv.innerHTML = `
                <i class="fas fa-${this.getIconForAlertType(type)} me-2"></i>
                ${message}
            `;
            resultDiv.classList.remove('d-none');
            
            // Auto hide after 5 seconds
            setTimeout(() => {
                resultDiv.classList.add('d-none');
            }, 5000);
        }
    }

    getIconForAlertType(type) {
        const icons = {
            'success': 'check-circle',
            'info': 'info-circle',
            'warning': 'exclamation-triangle',
            'danger': 'times-circle'
        };
        return icons[type] || 'info-circle';
    }

    handleFormSubmission(event) {
        const form = event.target;
        const districtSelect = form.querySelector('select[name="district"]');
        
        if (!districtSelect || !districtSelect.value) {
            event.preventDefault();
            this.showNotification('Please select a district.', 'danger');
            districtSelect.focus();
            return;
        }

        // Add loading state to button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<div class="loading me-2"></div> Loading...';
            submitBtn.disabled = true;

            // Revert after 2 seconds (in case page takes time to load)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        }

        // Cache the selection
        this.cacheDistrictSelection(districtSelect.value);
    }

    cacheDistrictSelection(districtCode) {
        if (typeof(Storage) !== "undefined") {
            localStorage.setItem('lastSelectedDistrict', districtCode);
            localStorage.setItem('lastSelectionTime', new Date().toISOString());
        }
    }

    loadCachedData() {
        if (typeof(Storage) !== "undefined") {
            const lastDistrict = localStorage.getItem('lastSelectedDistrict');
            const lastSelectionTime = localStorage.getItem('lastSelectionTime');
            
            if (lastDistrict && lastSelectionTime) {
                const selectionTime = new Date(lastSelectionTime);
                const now = new Date();
                const hoursDiff = (now - selectionTime) / (1000 * 60 * 60);
                
                // Only auto-select if within 24 hours
                if (hoursDiff < 24) {
                    const districtSelect = document.getElementById('district');
                    if (districtSelect) {
                        districtSelect.value = lastDistrict;
                    }
                }
            }
        }
    }

    setupInputValidation() {
        // Add real-time validation to form inputs
        const inputs = document.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('invalid', (e) => {
                e.preventDefault();
                this.showValidationError(input);
            });
            
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    validateField(field) {
        if (!field.checkValidity()) {
            this.showValidationError(field);
        } else {
            this.clearValidationError(field);
        }
    }

    showValidationError(field) {
        field.classList.add('is-invalid');
        
        // Create or update error message
        let errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.appendChild(errorDiv);
        }
        
        if (field.validity.valueMissing) {
            errorDiv.textContent = 'This field is required.';
        } else if (field.validity.typeMismatch) {
            errorDiv.textContent = 'Please enter a valid value.';
        }
    }

    clearValidationError(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 1050;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Utility function to format numbers
    static formatNumber(number) {
        return new Intl.NumberFormat('en-IN').format(number);
    }

    // Utility function to format currency
    static formatCurrency(amount) {
        if (amount >= 10000000) {
            return '₹' + (amount / 10000000).toFixed(2) + ' Cr';
        } else if (amount >= 100000) {
            return '₹' + (amount / 100000).toFixed(2) + ' L';
        } else {
            return '₹' + this.formatNumber(Math.round(amount));
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.mgnregaApp = new MGNREGAApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MGNREGAApp;
}