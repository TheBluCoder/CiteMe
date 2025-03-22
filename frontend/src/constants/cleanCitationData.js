/**
 * Citation Data Cleaner
 * Utility function to clean and prepare citation data for API submission
 */

// UI-specific keys that should be excluded from API requests
const EXCLUDED_KEYS = ['showOptionalFields', 'showMetadata'];

/**
 * Recursively cleans citation data by removing UI-specific fields
 * @param {Object|Array|*} data - The data to clean
 * @returns {Object|Array|*} Cleaned data without UI-specific fields
 */
export function cleanCitationData(data) {
    // Handle arrays recursively
    if (Array.isArray(data)) {
        return data.map(cleanCitationData);
    }

    // Handle objects recursively
    if (data !== null && typeof data === 'object') {
        const cleanedObj = {};
        for (const [key, value] of Object.entries(data)) {
            // Skip UI-specific keys
            if (EXCLUDED_KEYS.includes(key)) continue;
            cleanedObj[key] = cleanCitationData(value);
        }
        return cleanedObj;
    }

    // Return primitive values as is
    return data;
}
