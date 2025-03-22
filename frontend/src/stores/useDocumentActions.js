/**
 * Document Actions Module
 * Provides functionality for document printing and saving operations
 */

import { Document, Packer, Paragraph, TextRun } from 'docx';
import { saveAs } from 'file-saver';

// Print-specific styles
const PRINT_STYLES = `
    @media print {
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            line-height: 1.5;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 20px;
        }
        h2 {
            font-size: 20px;
            margin-top: 30px;
        }
    }
`;

/**
 * Prints the document content in a new window
 * @param {string} contentTitle - The title of the document
 * @param {string|HTMLElement} contentBody - The content to print
 */
export const printContent = (contentTitle, contentBody) => {
    // Open a new window
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        console.error('Print window could not be opened - pop-up may be blocked');
        return;
    }

    const doc = printWindow.document;

    // Setup document head
    const head = doc.head || doc.createElement('head');
    if (!doc.head) {
        doc.documentElement.appendChild(head);
    }

    // Set document title
    const titleEl = doc.createElement('title');
    titleEl.textContent = contentTitle;
    head.appendChild(titleEl);

    // Add print styles
    const style = doc.createElement('style');
    style.textContent = PRINT_STYLES;
    head.appendChild(style);

    // Setup document body
    const body = doc.body || doc.createElement('body');
    if (!doc.body) {
        doc.documentElement.appendChild(body);
    }

    // Add content to body
    if (typeof contentBody === 'string') {
        body.innerHTML = `
            <h1>${contentTitle}</h1>
            ${contentBody}
        `;
    } else if (contentBody instanceof HTMLElement) {
        body.appendChild(doc.importNode(contentBody, true));
    } else {
        console.error('Unsupported content type for printing');
        return;
    }

    // Print after a brief delay to ensure content is rendered
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 250);
};

/**
 * Saves the document content as a Word document
 * @param {string} title - The title of the document
 * @param {string} content - The content to save
 */
export const saveContent = (title, content) => {
    const doc = new Document({
        sections: [
            {
                properties: {},
                children: [
                    // Title
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: title,
                                bold: true,
                                size: 32,
                                font: 'Arial'
                            }),
                        ],
                        spacing: {
                            after: 400
                        }
                    }),
                    // Content
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: content,
                                size: 24,
                                font: 'Arial'
                            }),
                        ],
                        spacing: {
                            line: 360
                        }
                    }),
                ],
            },
        ],
    });

    Packer.toBlob(doc)
        .then((blob) => {
            saveAs(blob, `${title}.docx`);
        })
        .catch((error) => {
            console.error('Error saving document:', error);
        });
};
