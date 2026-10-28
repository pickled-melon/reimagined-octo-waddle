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
  showFilter: { type: Boolean, default: true },
  stats: { type: Object, default: null },
  statsLabels: { type: Object, default: () => ({ avg: 'Ср. значение', max: 'Макс', min: 'Мин' }) }
});

const emit = defineEmits(['update:selectedUserId', 'update:currentPage']);
</script>

<template>
  <div class="page-grid">
    <div class="top-panel">
      <div class="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-3">
        <div class="d-flex align-items-center gap-3 flex-wrap">
          <h1 class="h3 mb-0"><i :class="['bi', icon, 'me-2']"></i>{{ title }}</h1>
          
          <div v-if="stats" class="d-flex gap-3 text-muted small border-start ps-3">
            <span>Всего: <strong>{{ stats.count }}</strong></span>
            <span v-if="stats.avg !== null && stats.avg !== undefined">{{ statsLabels.avg }}: <strong>{{ stats.avg.toFixed(1) }}</strong></span>
            <span v-if="stats.max !== null && stats.max !== undefined">{{ statsLabels.max }}: <strong>{{ stats.max }}</strong></span>
            <span v-if="stats.min !== null && stats.min !== undefined">{{ statsLabels.min }}: <strong>{{ stats.min }}</strong></span>
          </div>
        </div>
        
        <div class="d-flex gap-3 align-items-center">
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
        </div>
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