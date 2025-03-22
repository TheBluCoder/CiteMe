<script setup>
import { onMounted, computed } from 'vue';
import CitationFormLayout from '@/components/Forms/CitationFormLayout.vue';
import FormAddBtn from '@/components/Forms/formAddBtn.vue';
import FormRemoveBtn from '@/components/Forms/FormRemoveBtn.vue';
import { useCitationFormActions } from '@/stores/useCitationFormActions.js';
import useFormDataFormat from '@/stores/useFormDataFormat.js';
import { useToast } from 'vue-toastification';

const props = defineProps({
    maxSources: Number,
});

const toast = useToast();

const sourceTemplate = {
    content: '',
    title: '',
    authors: '',
    url: '',
    type: '',
    accessDate: new Date().toISOString().split('T')[0],
    publishedDate: new Date().toISOString().split('T')[0],
    showMetadata: false,
};

const formData = useFormDataFormat('source', sourceTemplate);

const toggleMetadata = (index) => {
    formData.value.sources[index].showMetadata =
        !formData.value.sources[index].showMetadata;
};

const numOfSources = computed(() => {
    return formData.value.sources.length;
});

const addNewSource = () => {
    if (formData.value.sources.length < props.maxSources) {
        formData.value.sources.push({ ...sourceTemplate });
    }
};

const { save, removeSource } = useCitationFormActions(
    formData.value.formType,
    formData,
);

onMounted(() => {
    const storedFormData = localStorage.getItem('citationFormData');
    if (storedFormData) {
        const parsed = JSON.parse(storedFormData);
        if (parsed.type === 'source') {
            formData.value = parsed;
        }
    }
});
</script>

<template>
    <div
        class="fixed left-0 top-0 z-50 h-screen w-screen place-content-center rounded-md  py-2"
    >
        <CitationFormLayout
            @save="
                save(`Citation${formData.formType}Form`)
                    ? $emit('close')
                    : toast.error('fill all required fields.')
            "
            @discard="$emit('close')"
        >
            <div
                v-for="(source, index) in formData.sources"
                :key="index"
                class="mb-3 border-b border-gray-300"
            >
                <div class="mb-4 mt-2">
                    <label class="block text-sm font-medium text-gray-700">
                        <span class="text-gray-400">{{ index + 1 }} . </span
                        >Source Content
                        <textarea
                            v-model="source.content"
                            class="w-full rounded-md border-indigo-200 bg-white/50 py-1 pl-2 text-sm"
                            rows="18"
                            required
                            maxLength="70000"
                        ></textarea>
                    </label>
                </div>

                <div class="mb-4">
                    <button
                        type="button"
                        class="rounded-md border-indigo-200 bg-white/50 px-4 py-1 text-sm"
                        @click="toggleMetadata(index)"
                    >
                        {{ source.showMetadata ? 'Hide' : 'Show' }} Metadata
                    </button>
                </div>

                <div v-if="source.showMetadata" class="mb-4 grid gap-4">
                    <label class="block text-sm">
                        Title <span class="text-red-500">*</span>
                        <input
                            v-model="source.title"
                            type="text"
                            class="w-full p-2 rounded-md border-indigo-200 bg-white/50"
                            required
                            placeholder="title Of the source"
                            maxlength="50"
                        />
                    </label>
                    <label class="block text-sm">
                        Authors <span class="text-red-500">*</span>
                        <input
                            v-model="source.authors"
                            type="text"
                            class="w-full rounded-md p-2 border-indigo-200 bg-white/50"
                            placeholder="John Doe, Jane Doe et al"
                            required
                            maxlength="30"
                        />
                    </label>
                    <label class="block text-sm">
                        URL
                        <input
                            v-model="source.url"
                            type="url"
                            class="w-full p-2 rounded-md border-indigo-200 bg-white/50"
                            placeholder="https://www.example.com"
                            maxlength="50"
                        />
                    </label>
                    <label class="block text-sm">
                        Type <span class="text-red-500">*</span>
                        <input
                            v-model="source.sourceType"
                            type="text"
                            class="w-full rounded-md p-2 border-indigo-200 bg-white/50"
                            placeholder="journal, website, book etc"
                            maxlength="20"
                        />
                    </label>
                    <label class="block text-sm">
                        Published Date <span class="text-red-500">*</span>
                        <input
                            v-model="source.publishedDate"
                            type="date"
                            class="w-full rounded-md p-2 border-indigo-200 bg-white/50"
                        />
                    </label>
                    <label class="block text-sm">
                        Access Date <span class="text-red-500">*</span>
                        <input
                            v-model="source.accessDate"
                            type="date"
                            class="w-full rounded-md p-2 border-indigo-200 bg-white/50"
                        />
                    </label>
                </div>

                <div class="mb-4 flex justify-end gap-1">
                    <form-add-btn
                        @add="addNewSource"
                        :disable-add-btn="numOfSources === maxSources"
                    />
                    <form-remove-btn
                        @remove="removeSource(index)"
                        :disable-remove-btn="numOfSources === 1"
                    />
                </div>
            </div>
        </CitationFormLayout>
    </div>
</template>
