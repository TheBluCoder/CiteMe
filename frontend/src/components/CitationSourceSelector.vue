<script setup>
import { ref } from 'vue';
import CitationWebForm from '@/components/Forms/CitationWebForm.vue';
import CitationSourceForm from '@/components/Forms/CitationSourceForm.vue';
import CustomDropdown from '@/components/CustomDropdown.vue';
import { GlobeIcon, TextIcon, BotIcon } from 'lucide-vue-next';

const selectedForm = defineModel('selectedForm');
const showWebForm = ref(false);
const showSourceForm = ref(false);

const citationSourceOptions = [
    { value: 'auto', label: 'Auto Cite', icon: BotIcon },
    {
        value: 'web',
        label: 'Cite from web',
        action: () => (showWebForm.value = true),
        icon: GlobeIcon,
    },
    {
        value: 'source',
        label: 'Cite from source',
        action: () => (showSourceForm.value = true),
        icon: TextIcon,
    },
];

// const handleSourceChange = (newValue) => {
//     showForm.value = newValue !== 'auto';
// };
const maxSources = 5;
</script>

<template>
    <div class="mx-1 flex items-center space-x-2">
        <label
            class="mx-auto flex items-center space-x-1 text-sm font-medium text-gray-700"
        >
            <span class="whitespace-nowrap">Citation Source </span>
            <CustomDropdown
                :options="citationSourceOptions"
                @option-selected="selectedForm = $event"
            ></CustomDropdown>
        </label>
        <div class="mt-4">
            <keep-alive>
              <Transition name="fade">

                <CitationWebForm
                    v-show="showWebForm"
                    @close="showWebForm = false"
                    :max-sources="maxSources"
                />
              </Transition>
            </keep-alive>

            <keep-alive>
                <CitationSourceForm
                    v-if="showSourceForm"
                    @close="showSourceForm = false"
                    :max-sources="maxSources"
                />
            </keep-alive>
        </div>
    </div>
</template>
