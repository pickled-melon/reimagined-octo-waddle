<script setup>
import { computed } from 'vue';

const props = defineProps({
  current: { type: Number, required: true },
  total: { type: Number, required: true },
  pageSize: { type: Number, default: 20 },
});

const emit = defineEmits(['update:current']);

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)));

const pages = computed(() => {
  const maxVisible = 5;
  let start = Math.max(1, props.current - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages.value, start + maxVisible - 1);
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1);
  }
  const arr = [];
  for (let i = start; i <= end; i++) {
    arr.push(i);
  }
  return arr;
});

function goTo(page) {
  if (page >= 1 && page <= totalPages.value && page !== props.current) {
    emit('update:current', page);
  }
}
</script>

<template>
  <nav v-if="total > pageSize" class="d-flex justify-content-between align-items-center mt-3 flex-wrap gap-2">
    <span class="text-muted small">
      Всего: {{ total }} · стр. {{ current }} из {{ totalPages }}
    </span>
    <ul class="pagination mb-0">
      <li class="page-item" :class="{ disabled: current === 1 }">
        <button class="page-link" @click="goTo(current - 1)">&laquo;</button>
      </li>
      <li v-for="p in pages" :key="p" class="page-item" :class="{ active: p === current }">
        <button class="page-link" @click="goTo(p)">{{ p }}</button>
      </li>
      <li class="page-item" :class="{ disabled: current === totalPages }">
        <button class="page-link" @click="goTo(current + 1)">&raquo;</button>
      </li>
    </ul>
  </nav>
</template>