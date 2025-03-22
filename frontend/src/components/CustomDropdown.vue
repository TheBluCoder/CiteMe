<template>
  <div class="relative w-48 rounded-t-lg border border-gray-100 lg:w-52 bg-white">
      <button
          type="button"
          @click="toggleDropdown"
          class="flex w-full items-center gap-2 p-2 transition-all duration-300 rounded-t-lg hover:bg-gray-200"
      >
          <span v-show="!open" class="mx-1 w-full text-start">{{
              selected ? selected.label : 'Select an option'
          }}</span>
          <component :is="open ? ChevronRight : ChevronDown" class="h-5 w-5 transition-all duration-300"/>
      </button>
      <Transition name="fade">
          <div v-if="open" class="absolute left-0 z-50 w-full bg-inherit">
              <button
                  v-for="option in options"
                  :key="option.value"
                  @click="selectOption(option)"
                  class="group flex w-full justify-between border-t border-gray-200 px-2 py-2 text-start duration-300 hover:bg-indigo-100 hover:text-green-600 hover:cursor-pointer"
              >
                  <span>{{ option.label }}</span>
                  <component
                      :is="option.icon"
                      class="h-5 w-10 text-gray-400 group-hover:text-gray-600"
                  />
              </button>
          </div>
      </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { ChevronDown, ChevronRight } from 'lucide-vue-next';
const emits = defineEmits(['optionSelected']);

defineProps({
  options: {
      FormType: Array,
      required: true,
  },
});

const open = ref(false);
const selected = ref(null);

function toggleDropdown() {
  open.value = !open.value;
}

function selectOption(option) {
  selected.value = option;
  open.value = false;
  if (option?.action) option.action();
  emits('optionSelected', `Citation${option.value}Form`);
}
</script>

<style scoped></style>
