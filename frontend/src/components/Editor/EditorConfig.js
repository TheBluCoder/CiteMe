import CharacterCount from '@tiptap/extension-character-count';
import { Placeholder } from '@tiptap/extension-placeholder';
import TextAlign from '@tiptap/extension-text-align';
import Underline from '@tiptap/extension-underline';
import StarterKit from '@tiptap/starter-kit';
import { useEditor } from '@tiptap/vue-3';
import { ref } from 'vue';

export function useEditorConfig(initialContent) {
    const wordCount = ref(0);
    const characterCount = ref(0);
    const characterLimit = 12000;

    const editor = useEditor({
        autofocus: true,
        content: initialContent,
        extensions: [
            StarterKit.configure({
                heading: {
                    levels: [1, 2],
                    HTMLAttributes: {
                        class: 'font-bold',
                    },
                },
                paragraph: {
                    HTMLAttributes: {
                        style: 'margin: 0; line-height: 1.4;', // Inline styles for custom spacing
                    },
                },
            }),
            Placeholder.configure({
                placeholder: 'Start typing ...',
            }),
            CharacterCount.configure({
                limit: characterLimit,
            }),
            Underline,
            TextAlign.configure({
                types: ['heading', 'paragraph'],
            }),
        ],
        onUpdate: ({ editor }) => {
            const text = editor.getText();
            wordCount.value = text
                .split(/\s+/)
                .filter((word) => word.length > 0).length;
            characterCount.value = text.replace(/\n/g, '').length;
        },
    });
    return {
        characterCount,
        characterLimit,
        editor,
        wordCount,
    };
}
