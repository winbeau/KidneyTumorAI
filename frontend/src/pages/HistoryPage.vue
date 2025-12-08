<script setup lang="ts">
import {
  NCard,
  NDataTable,
  NButton,
  NSpace,
  NPopconfirm,
  NTag,
  NEmpty,
  useMessage,
  useDialog,
} from 'naive-ui'
import type { DataTableColumns, DataTableRowKey } from 'naive-ui'
import { h, onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getHistoryList, deleteHistoryRecord, batchDeleteHistory } from '@/api/history'
import { startInferenceTask } from '@/api/inference'
import type { HistoryRecord } from '@/api/types'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

// 数据
const loading = ref(false)
const data = ref<HistoryRecord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const selectedRowKeys = ref<DataTableRowKey[]>([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getHistoryList(page.value, pageSize.value)
    data.value = res.records
    total.value = res.total
  } catch (e: any) {
    message.error('加载失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

// 初始加载
onMounted(loadData)

// 格式化体积
const formatVolume = (mm3?: number) => {
  if (mm3 === undefined || mm3 === null) return '-'
  if (mm3 > 1000000) {
    return `${(mm3 / 1000000).toFixed(2)} cm³`
  }
  return `${mm3.toFixed(0)} mm³`
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

// 表格列
const columns: DataTableColumns<HistoryRecord> = [
  {
    type: 'selection',
  },
  {
    title: '文件名',
    key: 'filename',
    ellipsis: { tooltip: true },
  },
  {
    title: '上传时间',
    key: 'uploadTime',
    width: 180,
    render: (row) => formatTime(row.uploadTime),
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      const map: Record<string, { type: 'default' | 'success' | 'warning' | 'error', label: string }> = {
        completed: { type: 'success', label: '成功' },
        processing: { type: 'warning', label: '处理中' },
        queued: { type: 'warning', label: '待开始' },
        failed: { type: 'error', label: '失败' },
      }
      const { type, label } = map[row.status] || { type: 'default', label: row.status }
      return h(NTag, { type, size: 'small' }, () => label)
    },
  },
  {
    title: '肾脏体积',
    key: 'kidneyVolume',
    width: 120,
    render: (row) => row.stats ? formatVolume(row.stats.kidneyVolume) : '-',
  },
  {
    title: '肿瘤体积',
    key: 'tumorVolume',
    width: 120,
    render: (row) => row.stats ? formatVolume(row.stats.tumorVolume) : '-',
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    fixed: 'right',
    render: (row) => {
      const actions: ReturnType<typeof h>[] = []
      if (row.status === 'queued') {
        actions.push(h(NButton, {
          size: 'small',
          type: 'primary',
          ghost: true,
          onClick: () => handleStart(row.id),
        }, () => '开始推理'))
      }
      actions.push(h(NButton, {
        size: 'small',
        type: 'primary',
        ghost: true,
        disabled: row.status !== 'completed',
        onClick: () => viewResult(row.id),
      }, () => '查看'))
      actions.push(h(NPopconfirm, {
        onPositiveClick: () => handleDelete(row.id),
      }, {
        trigger: () => h(NButton, { size: 'small', type: 'error', ghost: true }, () => '删除'),
        default: () => '确定删除此记录？',
      }))
      return h(NSpace, { size: 'small' }, () => actions)
    },
  },
]

// 查看结果
const viewResult = (id: string) => {
  router.push(`/viewer/${id}`)
}

const pagination = computed(() => ({
  page: page.value,
  pageSize: pageSize.value,
  itemCount: total.value,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: handlePageChange,
  onUpdatePageSize: (size: number) => { pageSize.value = size; page.value = 1; loadData() },
}))

// 启动推理
const handleStart = async (id: string) => {
  try {
    await startInferenceTask(id)
    message.success('已开始推理')
    loadData()
  } catch (e: any) {
    message.error('启动失败: ' + e.message)
  }
}

// 删除记录
const handleDelete = async (id: string) => {
  try {
    await deleteHistoryRecord(id)
    message.success('删除成功')
    loadData()
  } catch (e: any) {
    message.error('删除失败: ' + e.message)
  }
}

// 批量删除
const handleBatchDelete = () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请先选择要删除的记录')
    return
  }

  dialog.warning({
    title: '批量删除',
    content: `确定删除选中的 ${selectedRowKeys.value.length} 条记录？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const ids = selectedRowKeys.value.map((key) => key.toString())
        await batchDeleteHistory(ids)
        message.success('删除成功')
        selectedRowKeys.value = []
        loadData()
      } catch (e: any) {
        message.error('删除失败: ' + e.message)
      }
    },
  })
}

// 分页变化
const handlePageChange = (p: number) => {
  page.value = p
  loadData()
}

// 行选择
const handleSelectionChange = (keys: DataTableRowKey[]) => {
  selectedRowKeys.value = keys
}
</script>

<template>
  <NCard title="历史记录">
    <template #header-extra>
      <NSpace>
        <NButton
          type="error"
          ghost
          :disabled="selectedRowKeys.length === 0"
          @click="handleBatchDelete"
        >
          <template #icon>
            <div class="i-carbon-trash-can" />
          </template>
          批量删除 ({{ selectedRowKeys.length }})
        </NButton>
        <NButton @click="loadData">
          <template #icon>
            <div class="i-carbon-refresh" />
          </template>
          刷新
        </NButton>
      </NSpace>
    </template>

    <NDataTable
      :columns="columns"
      :data="data"
      :loading="loading"
      :row-key="(row: HistoryRecord) => row.id"
      :checked-row-keys="selectedRowKeys"
      :pagination="pagination"
      @update:checked-row-keys="handleSelectionChange"
    >
      <template #empty>
        <NEmpty description="暂无历史记录">
          <template #extra>
            <NButton type="primary" @click="router.push('/')">
              上传影像
            </NButton>
          </template>
        </NEmpty>
      </template>
    </NDataTable>
  </NCard>
</template>
