<script setup>
import Pagination from '@/components/Pagination.vue';

defineProps({
  title: { type: String, required: true },
  icon: { type: String, required: true },
  totalCount: { type: Number, required: true },
  currentPage: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  users: { type: Array, default: () => [] },
  selectedUserId: { type: [String, Number], default: "" },
  isSuperuser: { type: Boolean, default: false },
  showFilter: { type: Boolean, default: true }
});

const emit = defineEmits(['update:selectedUserId', 'update:currentPage']);
</script>

<template>
  <div class="page-grid">
    <div class="top-panel">
      <div class="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-3">
        <h1 class="h3 mb-0"><i :class="['bi', icon, 'me-2']"></i>{{ title }}</h1>
        
        <div v-if="isSuperuser && showFilter" class="d-flex align-items-center gap-2">
          <label class="form-label mb-0 fw-semibold text-muted">Фильтр по автору:</label>
          <select 
            :value="selectedUserId" 
            @change="emit('update:selectedUserId', $event.target.value)" 
            class="form-select border-primary" 
            style="width: 200px;"
          >
            <option value="">Все пользователи</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
          </select>
        </div>

        <span class="badge text-bg-secondary rounded-pill px-3 py-2">Всего: {{ totalCount }}</span>
      </div>

      <slot name="form"></slot>
    </div>

    <div class="scroll-area">
      <slot name="content"></slot>
    </div>

    <div class="bottom-panel mt-3">
      <Pagination 
        :current="currentPage" 
        :total="totalCount" 
        :page-size="pageSize" 
        @update:current="emit('update:currentPage', $event)" 
      />
    </div>

    <slot name="modals"></slot>
  </div>
</template>

<style scoped>
.page-grid {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: 100%;
  padding: 1.5rem;
  overflow: hidden;
}

.scroll-area {
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
}
</style>