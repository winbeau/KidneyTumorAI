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
import type { DataTableColumns } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getHistoryList, deleteHistoryRecord, batchDeleteHistory } from '@/api/history'
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
const selectedRowKeys = ref<string[]>([])

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
const formatVolume = (mm3: number) => {
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
      return h(NTag, {
        type: row.status === 'completed' ? 'success' : 'error',
        size: 'small',
      }, () => row.status === 'completed' ? '成功' : '失败')
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
    width: 150,
    fixed: 'right',
    render: (row) => {
      return h(NSpace, { size: 'small' }, () => [
        h(NButton, {
          size: 'small',
          type: 'primary',
          ghost: true,
          disabled: row.status !== 'completed',
          onClick: () => viewResult(row.id),
        }, () => '查看'),
        h(NPopconfirm, {
          onPositiveClick: () => handleDelete(row.id),
        }, {
          trigger: () => h(NButton, { size: 'small', type: 'error', ghost: true }, () => '删除'),
          default: () => '确定删除此记录？',
        }),
      ])
    },
  },
]

// 查看结果
const viewResult = (id: string) => {
  router.push(`/viewer/${id}`)
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
        await batchDeleteHistory(selectedRowKeys.value)
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
const handleSelectionChange = (keys: string[]) => {
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
      :pagination="{
        page,
        pageSize,
        itemCount: total,
        showSizePicker: true,
        pageSizes: [10, 20, 50],
        onChange: handlePageChange,
        onUpdatePageSize: (size: number) => { pageSize = size; loadData() },
      }"
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
