<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import type { SubscribeOrder } from '@/types'

const loading = ref(false)
const list = ref<SubscribeOrder[]>([])
const total = ref(0)
const page = ref(1)

const keyword = ref('')
const status = ref('')
const channel = ref('')

const remarkDialogVisible = ref(false)
const actionLoading = ref(false)
const currentAction = ref<'approve' | 'reject'>('approve')
const currentOrder = ref<SubscribeOrder | null>(null)
const remark = ref('')

async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: 20 }
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    if (status.value) params.status = status.value
    if (channel.value) params.channel = channel.value
    const res = await api.get('/admin/payments', { params })
    list.value = (res.data.list || []) as SubscribeOrder[]
    total.value = Number(res.data.total || 0)
  } catch {
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function openAction(row: SubscribeOrder, action: 'approve' | 'reject') {
  currentOrder.value = row
  currentAction.value = action
  remark.value = row.remark || ''
  remarkDialogVisible.value = true
}

async function submitAction() {
  if (!currentOrder.value) return
  actionLoading.value = true
  try {
    const endpoint = currentAction.value === 'approve' ? 'approve' : 'reject'
    await api.put(`/admin/payments/${currentOrder.value.id}/${endpoint}`, { remark: remark.value.trim() })
    ElMessage.success(currentAction.value === 'approve' ? '订单已通过并开通订阅' : '订单已驳回')
    remarkDialogVisible.value = false
    await fetchList()
  } catch {
    // handled globally
  } finally {
    actionLoading.value = false
  }
}

async function quickApprove(row: SubscribeOrder) {
  try {
    await ElMessageBox.confirm(`确认通过订单 ${row.order_no || row.id} 并开通订阅吗？`, '审核订单', { type: 'warning' })
    await api.put(`/admin/payments/${row.id}/approve`, { remark: row.remark || '' })
    ElMessage.success('订单已通过并开通订阅')
    await fetchList()
  } catch {
    // cancel
  }
}

function formatAmount(value: number | string | null) {
  if (value == null || value === '') return '-'
  const num = Number(value)
  return Number.isFinite(num) ? `¥${Number.isInteger(num) ? num : num.toFixed(2)}` : String(value)
}

function statusTag(statusValue: SubscribeOrder['status']) {
  if (statusValue === 'success') return 'success'
  if (statusValue === 'failed') return 'danger'
  return 'warning'
}

onMounted(fetchList)
</script>

<template>
  <div class="space-y-6">
    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
      <div class="flex flex-wrap items-center gap-3">
        <el-input v-model="keyword" placeholder="搜索订单号 / 用户昵称 / 手机 / 邮箱" clearable style="width: 280px" @keyup.enter="fetchList" />
        <el-select v-model="status" clearable placeholder="订单状态" style="width: 140px">
          <el-option label="待处理" value="pending" />
          <el-option label="已成功" value="success" />
          <el-option label="已驳回" value="failed" />
        </el-select>
        <el-select v-model="channel" clearable placeholder="支付渠道" style="width: 140px">
          <el-option label="微信" value="wechat" />
          <el-option label="支付宝" value="alipay" />
        </el-select>
        <el-button type="primary" @click="fetchList">查询</el-button>
      </div>

      <el-table :data="list" v-loading="loading" stripe border class="mt-6" style="width: 100%">
        <el-table-column prop="order_no" label="订单号" min-width="180" />
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="font-medium text-slate-900">{{ row.nickname || `用户 ${row.user_id}` }}</div>
            <div class="text-xs text-slate-500">{{ row.phone || row.email || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="套餐" width="120">
          <template #default="{ row }">
            <div>{{ row.plan_name || row.plan || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="channel" label="渠道" width="100" />
        <el-table-column label="金额" width="110">
          <template #default="{ row }">{{ formatAmount(row.amount) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="170" />
        <el-table-column prop="paid_at" label="生效时间" min-width="170" />
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" size="small" text type="success" @click="quickApprove(row)">通过</el-button>
            <el-button v-if="row.status === 'pending'" size="small" text type="danger" @click="openAction(row, 'reject')">驳回</el-button>
            <el-button v-else size="small" text type="primary" @click="openAction(row, row.status === 'success' ? 'approve' : 'reject')">备注</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > 20" class="mt-4 flex justify-end">
        <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" background @current-change="fetchList" />
      </div>
    </section>

    <el-dialog v-model="remarkDialogVisible" :title="currentAction === 'approve' ? '通过订单' : '驳回订单'" width="520px" destroy-on-close>
      <div class="mb-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
        <div>订单号：{{ currentOrder?.order_no || currentOrder?.id }}</div>
        <div>用户：{{ currentOrder?.nickname || currentOrder?.user_id }}</div>
        <div>金额：{{ formatAmount(currentOrder?.amount ?? null) }}</div>
      </div>
      <el-form label-position="top">
        <el-form-item label="备注">
          <el-input v-model="remark" type="textarea" :rows="4" placeholder="填写处理备注，可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="remarkDialogVisible = false">取消</el-button>
        <el-button :type="currentAction === 'approve' ? 'success' : 'danger'" :loading="actionLoading" @click="submitAction">
          {{ currentAction === 'approve' ? '确认通过' : '确认驳回' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>
