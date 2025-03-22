/**
 * Editor Toolbar Constants
 * Defines the configuration and actions for the rich text editor toolbar
 * Including text formatting, alignment, and history controls
 */

import {
  Bold,
  Italic,
  Redo,
  StrikethroughIcon,
  Underline,
  Undo,
  AlignRight,
  AlignLeft,
  AlignCenter,
  AlignJustify,
} from 'lucide-vue-next';

/**
 * Text formatting button configurations
 * Each button includes an icon, action, active state check, and tooltip
 */
export const formatButtons = [
  {
      icon: Bold,
      action: (editor) => editor?.chain().focus().toggleBold().run(),
      isActive: (editor) => editor?.isActive('bold'),
      tooltip: 'Bold',
  },
  {
      icon: Italic,
      action: (editor) => editor?.chain().focus().toggleItalic().run(),
      isActive: (editor) => editor?.isActive('italic'),
      tooltip: 'Italic',
  },
  {
      icon: Underline,
      action: (editor) => editor?.chain().focus().toggleUnderline().run(),
      isActive: (editor) => editor?.isActive('underline'),
      tooltip: 'Underline',
  },
  {
      icon: StrikethroughIcon,
      action: (editor) => editor?.chain().focus().toggleStrike().run(),
      isActive: (editor) => editor?.isActive('strike'),
      tooltip: 'Strikethrough',
  },
];

/**
 * History control button configurations
 * Includes undo and redo functionality
 */
export const historyButtons = [
  {
      icon: Undo,
      action: (editor) => editor?.chain().focus().undo().run(),
      isDisabled: (editor) => !editor?.can().undo(),
      tooltip: 'Undo',
  },
  {
      icon: Redo,
      action: (editor) => editor?.chain().focus().redo().run(),
      isDisabled: (editor) => !editor?.can().redo(),
      tooltip: 'Redo',
  },
];

/**
 * Updates the heading style of the selected text
 * @param {Editor} editor - The TipTap editor instance
 * @param {string} value - The heading type to apply ('paragraph', 'h1', 'h2')
 */
export const updateHeading = (editor, value) => {
    if (!editor) return;

    const headingActions = {
        paragraph: () => editor.chain().focus().setParagraph().run(),
        h1: () => editor.chain().focus().toggleHeading({ level: 1 }).run(),
        h2: () => editor.chain().focus().toggleHeading({ level: 2 }).run(),
    };

    headingActions[value]?.();
};

/**
 * Text alignment button configurations
 * Controls text alignment options (left, center, right, justify)
 */
export const alignmentButtons = [
  {
      icon: AlignLeft,
      action: (editor) => editor?.chain().focus().setTextAlign('left').run(),
      isActive: (editor) => editor?.isActive({ textAlign: 'left' }),
      tooltip: 'Align Left',
  },
  {
      icon: AlignCenter,
      action: (editor) => editor?.chain().focus().setTextAlign('center').run(),
      isActive: (editor) => editor?.isActive({ textAlign: 'center' }),
      tooltip: 'Align Center',
  },
  {
      icon: AlignRight,
      action: (editor) => editor?.chain().focus().setTextAlign('right').run(),
      isActive: (editor) => editor?.isActive({ textAlign: 'right' }),
      tooltip: 'Align Right',
  },
  {
      icon: AlignJustify,
      action: (editor) => editor?.chain().focus().setTextAlign('justify').run(),
      isActive: (editor) => editor?.isActive({ textAlign: 'justify' }),
      tooltip: 'Justify',
  },
];
