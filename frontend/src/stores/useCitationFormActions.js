/**
 * Citation Form Actions
 * Provides functionality for managing citation form data and validation
 */

/**
 * Hook for managing citation form actions
 * @param {string} formType - The type of citation form ('web', 'book', etc.)
 * @param {Ref<Object>} formData - Reactive form data object
 * @returns {Object} Form actions and data
 */
export function useCitationFormActions(formType, formData) {
    /**
     * Validates the citation form data
     * @returns {boolean} True if form is valid, false otherwise
     */
    const validateForm = () => {
        return formData.value.sources.every((source) => {
            // Required fields for all source types
            const baseValidation = Boolean(
                source.authors &&
                source.title &&
                source.sourceType &&
                source.publishedDate
            );

            // Additional validation for web sources
            if (formType === 'web') {
                return baseValidation && Boolean(source.url);
            }

            return baseValidation;
        });
    };

    /**
     * Saves form data to local storage
     * @param {string} key - Storage key for the form data
     * @returns {boolean} True if save was successful, false otherwise
     */
    const save = (key) => {
        if (!validateForm()) {
            return false;
        }
        try {
            localStorage.setItem(key, JSON.stringify(formData.value));
            return true;
        } catch (error) {
            console.error('Error saving form data:', error);
            return false;
        }
    };

    // const discard = (key) => {
    //     formData.value.sources = [{ ...initialTemplate }];
    //     localStorage.removeItem(key);
    //     return true;
    // };

    /**
     * Removes a source from the form data
     * @param {number} index - Index of the source to remove
     */
    const removeSource = (index) => {
        if (formData.value.sources.length > 1) {
            formData.value.sources.splice(index, 1);
        }
    };

    /**
     * Adds a new source to the form data
     * @param {Object} sourceTemplate - Template for the new source
     */
    const addSource = (sourceTemplate) => {
        formData.value.sources.push({ ...sourceTemplate });
    };

    return {
        formData,
        save,
        // discard,
        removeSource,
        addSource,
        validateForm
    };
}
