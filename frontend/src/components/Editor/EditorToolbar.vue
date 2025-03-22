<script setup>
import {
    formatButtons,
    historyButtons,
    updateHeading,
    alignmentButtons,
} from '@/stores/useEditorToolbarConstants.js';

const props = defineProps({
    modelValue: {
        type: String,
        required: true,
    },
    editor: {
        type: Object,
        required: true,
    },
});

const handleHeadingChange = (event) => {
    const value = event.target.value;
    updateHeading(props.editor, value);
    props.editor.commands.focus();
}
</script>

<template>
    <div class="flex items-center space-x-2 rounded-lg bg-white p-2 shadow">
        <select
            :value="modelValue"
            class="w-[20%] rounded border-gray-300 text-sm md:w-auto"
            @change="handleHeadingChange"
            name="fontOption"
        >
            <option value="paragraph">Normal text</option>
            <option value="h1">Heading 1</option>
            <option value="h2">Heading 2</option>
        </select>
        <div class="h-6 w-px bg-gray-300"></div>
        <div class="flex w-full items-center justify-between">
            <div class="flex items-center gap-4">
                <div class="flex-wrap">
                    <button
                        v-for="(item, index) in formatButtons"
                        :key="index"
                        @click="item.action(props.editor)"
                        class="mr-[2px] w-5 rounded p-1 hover:bg-gray-100"
                        :class="{
                            'bg-gray-100 text-blue-600': item.isActive(
                                props.editor,
                            ),
                        }"
                        :title="item.tooltip"
                    >
                        <component :is="item.icon" class="h-4 w-4" />
                    </button>
                </div>
                <div
                    class="flex justify-between divide-x divide-gray-400 self-end rounded-lg border border-gray-300 shadow-md"
                >
                    <button
                        v-for="(item, index) in alignmentButtons"
                        :key="index"
                        @click="item.action(props.editor)"
                        class="p-1 hover:cursor-pointer hover:bg-gray-100"
                        :class="{
                            'bg-gray-200 text-blue-600': item.isActive(
                                props.editor,
                            ),
                        }"
                        :title="item.tooltip"
                    >
                        <component :is="item.icon" class="h-4 w-4" />
                    </button>
                </div>
            </div>
            <div
                class="mx-0.5 flex divide-x divide-gray-400 rounded-lg border border-gray-400 shadow-md"
            >
                <button
                    v-for="(item, index) in historyButtons"
                    :key="index"
                    @click="item.action(props.editor)"
                    class="p-1 hover:cursor-pointer"
                    :class="{
                        'text-gray-500': item.isDisabled(props.editor),
                    }"
                    :title="item.tooltip"
                >
                    <component :is="item.icon" class="h-4 w-4" />
                </button>
            </div>
        </div>
    </div>
</template>

<style>
/* Add any component-specific styles here */
</style>
