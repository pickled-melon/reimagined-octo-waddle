import { ref, watch } from 'vue';
import axios from 'axios';
import useProfileStore from '@/stores/profileStore';
import { storeToRefs } from 'pinia';

export function useCrud(apiUrl) {
  const profileStore = useProfileStore();
  const { isSuperuser } = storeToRefs(profileStore);

  const items = ref([]);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const pageSize = 20;
  const loading = ref(false);
  const stats = ref(null);
  
  const users = ref([]);
  const selectedUserId = ref("");

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
    const r = await axios.get(url);
    items.value = r.data.results;
    totalCount.value = r.data.count;
    currentPage.value = page;
    loading.value = false;
  }

  watch(selectedUserId, () => {
    fetchData(1);
    fetchStats();
  });

  watch(currentPage, (newPage) => {
    fetchData(newPage);
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
    isSuperuser,
    fetchUsers,
    fetchData,
    fetchStats,
    onRemove
  };
}