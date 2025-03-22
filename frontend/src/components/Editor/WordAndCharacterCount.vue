<template>
  <div>
      <div class="text-right text-sm text-indigo-600">
          {{ wordCount }} words
      </div>

      <div class="flex items-center space-x-2">
          <span
              :class="{
                  'whitespace-nowrap text-xs': true,
                  'text-indigo-50': hideCharacterCount,
              }"
          >
              {{ characterCount + '/' + characterLimit }} chars
          </span>
          <div
              :class="{
                  'h-[3px] w-full rounded-lg': true,
                  'bg-green-400': characterCount <= greenRegion,
                  'bg-yellow-400':
                      characterCount > greenRegion &&
                      characterCount <= yellowRegion,
                  'bg-orange-300':
                      characterCount > yellowRegion &&
                      characterCount <= characterLimit,
                  'bg-red-500': characterCount === characterLimit,
                  'bg-transparent': hideBar,
              }"
          ></div>
      </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  wordCount: {
      FormType: Number,
      required: true,
  },
  characterCount: {
      FormType: Number,
      required: true,
  },
  characterLimit: {
      FormType: Number,
      required: true,
  },
  hideBar: {
      FormType: Boolean,
      default: false,
  },
  hideCharacterCount: {
      FormType: Boolean,
      default: false,
  },
});

const greenRegion = computed(() => props.characterLimit * 0.6);
const yellowRegion = computed(() => props.characterLimit * 0.75);
</script>