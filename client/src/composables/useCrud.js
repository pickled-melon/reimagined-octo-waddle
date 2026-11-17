import { ref, watch, provide } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import { storeToRefs } from 'pinia';

export const crudLoadingKey = Symbol('crudLoading');
export const crudSearchKey = Symbol('crudSearch');

export function useCrud(apiUrl) {
  const profileStore = useProfileStore();
  const { isSuperuser } = storeToRefs(profileStore);

  const items = ref([]);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const pageSize = 20;
  const loading = ref(false);
  const stats = ref(null);
  provide(crudLoadingKey, loading);
  
  const users = ref([]);
  const selectedUserId = ref("");
  const filters = ref({});
  const search = ref('');
  provide(crudSearchKey, search);

  async function fetchUsers() {
    if (isSuperuser.value) {
      const r = await axios.get('/api/profile/all/');
      users.value = r.data;
    }
  }

  async function fetchStats() {
    let url = `${apiUrl}stats/`;
    if (isSuperuser.value && selectedUserId.value) {
      url += `?user=${selectedUserId.value}`;
    }
    const r = await axios.get(url);
    stats.value = r.data;
  }

  async function fetchData(page = 1) {
    loading.value = true;
    let url = `${apiUrl}?page=${page}`;
    if (isSuperuser.value && selectedUserId.value) {
      url += `&user=${selectedUserId.value}`;
    }
    if (search.value) {
      url += '&search=' + encodeURIComponent(search.value);
    }
    for (const [key, value] of Object.entries(filters.value)) {
      if (value !== null && value !== undefined && value !== '') {
        url += '&' + key + '=' + value;
      }
    }
    const r = await axios.get(url);
    items.value = r.data.results;
    totalCount.value = r.data.count;
    if (currentPage.value !== page) currentPage.value = page;
    loading.value = false;
  }

  watch(selectedUserId, () => {
    fetchData(1);
    fetchStats();
  });

  watch(currentPage, (newPage) => {
    fetchData(newPage);
  });

  watch(filters, () => {
    fetchData(1);
  }, { deep: true });

  let searchTimer = null;
  watch(search, () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      if (currentPage.value !== 1) {
        currentPage.value = 1;
      } else {
        fetchData(1);
      }
    }, 300);
  });

  async function onRemove(id, confirmMessage) {
    if (!confirm(confirmMessage)) return;
    await axios.delete(`${apiUrl}${id}/`);
    const targetPage = items.value.length === 1 && currentPage.value > 1
      ? currentPage.value - 1
      : currentPage.value;
    await fetchData(targetPage);
    await fetchStats();
  }

  return {
    items,
    totalCount,
    currentPage,
    pageSize,
    loading,
    stats,
    users,
    selectedUserId,
    filters,
    search,
    isSuperuser,
    fetchUsers,
    fetchData,
    fetchStats,
    onRemove
  };
}