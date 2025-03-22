<script setup>
defineProps({
    icon: Function,
});
</script>

<template>
    <button
        class="flex gap-1 rounded-lg border border-gray-300 px-2 py-1 drop-shadow-xl transition-colors duration-300 hover:bg-indigo-50"
    >
        <slot />
        <component :is="icon" class="w-[15px] text-gray-600" />
    </button>
</template>

<style scoped></style>