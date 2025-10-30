// Location-specific functionality
class LocationService {
    constructor() {
        this.geolocationSupported = 'geolocation' in navigator;
        this.init();
    }

    init() {
        this.setupGeolocationFallbacks();
    }

    setupGeolocationFallbacks() {
        // Add geolocation permission request handler
        if (this.geolocationSupported) {
            this.requestGeolocationPermission();
        }
    }

    requestGeolocationPermission() {
        // This is a passive permission request - will be triggered when user clicks location button
        console.log('Geolocation is supported by this browser.');
    }

    async getApproximateLocation() {
        // Fallback method using IP-based location
        try {
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();
            
            return {
                latitude: data.latitude,
                longitude: data.longitude,
                city: data.city,
                region: data.region,
                country: data.country_name,
                accuracy: 'low' // IP-based location has low accuracy
            };
        } catch (error) {
            console.error('IP-based location failed:', error);
            return null;
        }
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
        // Haversine formula to calculate distance between two coordinates
        const R = 6371; // Earth's radius in kilometers
        const dLat = this.deg2rad(lat2 - lat1);
        const dLon = this.deg2rad(lon2 - lon1);
        
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(this.deg2rad(lat1)) * Math.cos(this.deg2rad(lat2)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
        const distance = R * c; // Distance in km
        
        return distance;
    }

    deg2rad(deg) {
        return deg * (Math.PI/180);
    }

    // Cache location data to avoid repeated API calls
    cacheLocationData(key, data, expiryMinutes = 60) {
        if (typeof(Storage) !== "undefined") {
            const item = {
                data: data,
                expiry: new Date().getTime() + (expiryMinutes * 60 * 1000)
            };
            localStorage.setItem(`location_${key}`, JSON.stringify(item));
        }
    }

    getCachedLocationData(key) {
        if (typeof(Storage) !== "undefined") {
            const itemStr = localStorage.getItem(`location_${key}`);
            if (!itemStr) return null;
            
            const item = JSON.parse(itemStr);
            if (new Date().getTime() > item.expiry) {
                localStorage.removeItem(`location_${key}`);
                return null;
            }
            
            return item.data;
        }
        return null;
    }
}

// Initialize location service
document.addEventListener('DOMContentLoaded', () => {
    window.locationService = new LocationService();
});