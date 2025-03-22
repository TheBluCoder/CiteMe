/**
 * Preview Toolbar Store
 * Manages the functionality for the document preview toolbar
 * Including copy, edit, save, and print actions
 */

import { printContent, saveContent } from '@/stores/useDocumentActions.js';
import { CopyIcon, Edit3Icon, PrinterIcon, SaveIcon } from 'lucide-vue-next';
import { inject } from 'vue';
import { useToast } from 'vue-toastification';

/**
 * Hook for managing preview toolbar actions and state
 * @returns {Object} Toolbar configuration and actions
 */
export function usePreviewToolBar() {
    const previewContent = inject('previewContent');
    const emits = inject('emits');
    const toast = useToast();

    /**
     * Combines formatted text and references into a single string
     * @returns {string} Combined content
     */
    const getCombinedContent = (includeHeading = false) => {
        const formattedText = previewContent.value.content[0] || ' ';
        const references = previewContent.value.content[1] || ' ';
        return includeHeading
            ? `${formattedText}<h2>References</h2>\n${references}`
            : `${formattedText}\n\nReferences\n${references}`;
    };

    /**
     * Copies the formatted content to clipboard
     */
    const copyContent = async () => {
        try {
            await navigator.clipboard.writeText(getCombinedContent());
            toast.success('Content copied to clipboard!', {
                timeout: 2000,
                position: 'bottom-right',
            });
        } catch (error) {
            console.error('Copy failed:', error);
            toast.error('Failed to copy content');
        }
    };

    /**
     * Saves the document content to a file
     */
    const handleSave = () => {
        saveContent(
            previewContent.value.title,
            getCombinedContent()
        );
    };

    /**
     * Triggers edit mode for the document
     */
    const editContent = () => {
        emits('edit');
    };

    /**
     * Prints the document content
     */
    const handlePrint = () => {
        printContent(
            previewContent.value.title,
            getCombinedContent(true)
        );
    };

    /**
     * Toolbar button configurations
     */
    const PreviewToolBarConstants = [
        {
            icon: CopyIcon,
            text: 'Copy',
            action: copyContent,
            tooltip: 'Copy to clipboard'
        },
        {
            icon: Edit3Icon,
            text: 'Edit',
            action: editContent,
            tooltip: 'Edit document'
        },
        {
            icon: SaveIcon,
            text: 'Save',
            action: handleSave,
            tooltip: 'Save document'
        },
        {
            icon: PrinterIcon,
            text: 'Print',
            action: handlePrint,
            tooltip: 'Print document'
        },
    ];

    return { PreviewToolBarConstants };
}
