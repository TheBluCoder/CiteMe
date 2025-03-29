<script setup>
import {
    Menu,
    ToggleLeftIcon,
    ToggleRightIcon,
    PlayIcon,
} from 'lucide-vue-next';
import { useCitationStore } from '@/stores/citationStore';
import CiteMeLogo from '@/components/CiteMeLogo.vue';
// import { useRouter } from 'vue-router';

// const router = useRouter();
const store = useCitationStore();
const emit = defineEmits(['toggleSidebar', 'generateCitations', 'navigateToEditor', 'navigateToPreview']);

defineProps({
    disableBtn: Boolean,
});

// This needs to be a computed prop that watches the route
const showPreview = defineModel('showPreview', {
    required: true,
    default: false,
});

const handleToggleSidebar = () => {
    emit('toggleSidebar');
};

let title = defineModel('title');

const generateCitations = () => {
    emit('generateCitations');
};

const toggleView = () => {
    if (showPreview.value) {
        emit('navigateToEditor');
    } else {
        emit('navigateToPreview');
    }
};
</script>

<template>
    <div class="relative">
        <!-- Loading Banner -->
        <Transition
            enter-active-class="transition ease-out duration-200"
            enter-from-class="transform opacity-0 -translate-y-2"
            enter-to-class="transform opacity-100 translate-y-0"
            leave-active-class="transition ease-in duration-150"
            leave-from-class="transform opacity-100 translate-y-0"
            leave-to-class="transform opacity-0 -translate-y-2"
        >
            <div v-if="store.isCitationLoading" class="absolute inset-x-0 top-0 z-50">
                <div class="bg-gray-900/95 backdrop-blur-sm p-2 border-b border-gray-700/30">
                    <div class="flex items-center justify-center gap-2">
                        <div class="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-white"></div>
                        <p class="text-sm font-medium text-gray-200">Generating citations...</p>
                    </div>
                </div>
            </div>
        </Transition>

        <header class="bg-white shadow">
            <div class="flex items-center justify-between px-1 py-4 lg:p-4">
                <!-- Left side -->
                <div class="flex items-center space-x-4">
                    <button
                        class="rounded p-2 hover:bg-gray-100"
                        @click="handleToggleSidebar"
                    >
                        <Menu class="h-4 w-5" />
                    </button>

                    <div class="flex items-center h-6">
                        <CiteMeLogo />
                    </div>

                    <input
                        class="border-none text-gray-500 bg-white text-lg font-medium focus:ring-0 focus:border-none focus:outline-none hover:text-gray-800 hover:cursor-text focus:text-gray-800"
                        v-model="title"
                        name="docTitle"
                        type="text"
                        placeholder="Untitled"
                        required
                        maxlength="150"
                    />
                </div>

                <!-- Center text - only visible on md and up -->
                <div class="hidden md:block absolute left-1/2 transform -translate-x-1/2">
                    <h1 class="text-xl font-bold shimmer-container">
                        <span class="text-blue-500 relative shimmer-text">Cite</span><span class="text-purple-600 relative shimmer-text">ME</span>
                    </h1>
                </div>

                <!-- Right side -->
                <div class="flex items-center space-x-4">
                    <button
                        class="flex gap-2"
                        @click="toggleView"
                    >
                        <span
                            class="text-sm"
                            :class="{ 'text-gray-600': !showPreview }"
                            >preview</span
                        >
                        <component
                            :is="showPreview ? ToggleRightIcon : ToggleLeftIcon"
                            :class="{ 'text-green-400': showPreview }"
                            class="hover:cursor-pointer"
                        />
                    </button>
                    <button
                        class="hidden items-center rounded-lg bg-green-500 px-4 py-2 text-white hover:bg-green-600 md:flex md:gap-2"
                        :class="{ 'opacity-40': disableBtn }"
                        @click="generateCitations"
                        :disabled="disableBtn"
                    >
                        <span class="text-white">Cite Me</span>
                        <play-icon class="h-4 text-white" />
                    </button>
                    <div
                        id="citationStyleSelector"
                        class="hidden md:block"
                    ></div>
                </div>
            </div>
        </header>

        <!-- Mobile-only floating action button -->
        <div
            class="fixed bottom-6 left-0 z-20 flex w-full justify-center gap-4 bg-transparent md:hidden"
        >
            <button
                class="flex items-center gap-2 rounded-lg border bg-green-500 px-2"
                :class="{ 'opacity-40': disableBtn }"
                @click="generateCitations"
                :disabled="disableBtn"
            >
                <span class="text-white">Cite Me</span>
                <play-icon class="h-4 text-white" />
            </button>
            <!-- Mobile-only citation style selector -->
            <div>
                <div id="mobileCitationStyleSelector"></div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.shimmer-container {
    position: relative;
    overflow: hidden;
}

.shimmer-text {
    position: relative;
}

.shimmer-text::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.8) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% {
        left: -100%;
    }
    100% {
        left: 200%;
    }
}
</style>
