<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import WebFormFields from '@/components/Forms/webFormFields.vue';
import { useCitationFormActions } from '@/stores/useCitationFormActions.js';
import CitationFormLayout from '@/components/Forms/CitationFormLayout.vue';
import FormRemoveBtn from '@/components/Forms/FormRemoveBtn.vue';
import FormAddBtn from "@/components/Forms/FormAddBtn.vue";
import useFormDataFormat from '@/stores/useFormDataFormat.js';
import { ToggleLeftIcon, ToggleRightIcon } from 'lucide-vue-next';
import { useToast } from 'vue-toastification';

const toast = useToast();
const props = defineProps({
    maxSources: {
        FormType: Number,
        default: 7,
    },
});

const supplementUrls = ref(false);
const sourceTemplate = {
    url: '',
    authors: '',
    title: '',
    type: '', //e.g journal, book, website, article etc.
    publishedDate: new Date().toISOString().split('T')[0],
    showOptionalFields: false,
    doi: '',
    volume: '',
};
const effectiveMaxSources = computed(() => {
    return supplementUrls.value ? 3 : props.maxSources;
});

let getSupplementUrls = computed(() => {
    return supplementUrls.value;
});

const formData = useFormDataFormat('web', sourceTemplate);
formData.value.supplementUrls = getSupplementUrls;

const currentOpenOptionalFields = ref(null);

const addNewSource = () => {
    if (formData.value.sources.length < effectiveMaxSources.value) {
        formData.value.sources.push({ ...sourceTemplate });
    }
};

// Add watcher to remove excess sources when enhancement is enabled
watch(supplementUrls, (newValue) => {
    if (newValue && formData.value.sources.length > 3) {
        formData.value.sources.length = 3;
    }
});

const toggleOptionalFields = (index) => {
    if (currentOpenOptionalFields.value === index) {
        formData.value.sources[index].showOptionalFields =
            !formData.value.sources[index].showOptionalFields;
        return;
    }
    currentOpenOptionalFields.value = index;
    formData.value.sources.forEach((source, i) => {
        source.showOptionalFields = i === index;
    });
};

const { save, removeSource } = useCitationFormActions(
    formData.value.formType,
    formData,
);

const numOfSources = computed(() => {
    return formData.value.sources.length;
});

onMounted(() => {
    const storedFormData = localStorage.getItem('citationFormData');
    if (storedFormData) {
        const parsed = JSON.parse(storedFormData);
        if (parsed.type === 'web') {
            formData.value = parsed;
        }
    }
});
</script>

<template>
    <div

    >
        <CitationFormLayout
            @save="
                save(`Citation${formData.formType}Form`)
                    ? $emit('close')
                    : toast.error('fill all required fields.')
            "
            @discard="$emit('close')"
        >
            <!-- Add supplement url toggle at the top -->
            <div class="mb-4 flex items-center justify-end gap-2">
                <span class="text-sm text-gray-600">Find related URLs</span>
                <button
                    type="button"
                    class="flex items-center gap-2"
                    @click="supplementUrls = !supplementUrls"
                >
                    <component
                        :is="supplementUrls ? ToggleRightIcon : ToggleLeftIcon"
                        :class="{ 'text-green-400': supplementUrls }"
                        class="h-5 w-5"
                    />
                </button>
            </div>

            <!-- Add enhancement notice when enabled -->
            <div
                v-if="supplementUrls"
                class="mb-4 rounded-md bg-blue-50 p-3 text-sm text-blue-600"
            >
                You can add up to 3 URLs. We'll find related sources to
                supplement your citations.
            </div>

            <div
                v-for="(source, index) in formData.sources"
                :key="index"
                class="mb-3 border-b border-gray-300"
            >
                <div class="mb-4 mt-2">
                    <label
                        class="text-sm font-medium text-gray-700 lg:flex-shrink-0"
                        ><span class="text-gray-400">{{ index + 1 }} . </span
                        >URL
                        <input
                            name="url"
                            class="w-full rounded-md border-indigo-200 bg-white/50 py-1 pl-2 pr-8 text-sm backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500"
                            type="url"
                            v-model="source.url"
                            required
                            placeholder="https://www.example.com"
                            maxlength="50"
                        />
                    </label>
                </div>

                <div class="mb-4 flex justify-between">
                    <div>
                        <button
                            type="button"
                            class="mr-4 py-1 pl-2 pr-8 text-sm transition-colors duration-300"
                            :class="{
                                'text-green-600 hover:text-green-600/60':
                                    !source.showOptionalFields,
                                'text-red-500 hover:text-red-500/70':
                                    source.showOptionalFields,
                            }"
                            @click="toggleOptionalFields(index)"
                        >
                            {{ source.showOptionalFields ? 'Hide' : 'Show' }}
                        </button>
                    </div>
                    <div class="mb-4 flex justify-center gap-1">
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

                <div
                    v-if="source.showOptionalFields"
                    class="flex flex-wrap justify-between gap-x-4 gap-y-2"
                >
                    <WebFormFields
                        :source="source"
                        @update:authors="source.authors = $event"
                        @update:publishedDate="source.publishedDate = $event"
                        @update:title="source.title = $event"
                        @update:type="source.sourceType = $event"
                    />
                </div>
            </div>
        </CitationFormLayout>
    </div>
</template>

<style scoped></style>
