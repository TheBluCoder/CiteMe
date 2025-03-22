/**
 * Form Data Format Store
 * Provides a composable for managing citation form data structure
 */

import { ref } from 'vue';

/**
 * Creates a reactive form data structure for citations
 * @param {string} formType - The type of citation form
 * @param {Object} sourceTemplate - Template for source data structure
 * @returns {Ref<Object>} Reactive form data object
 */
export default function useFormDataFormat(formType, sourceTemplate) {
    return ref({
        sources: [{ ...sourceTemplate }],
        citationStyle: '',
        formType,
    });
}
