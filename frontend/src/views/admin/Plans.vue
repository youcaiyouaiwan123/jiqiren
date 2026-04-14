<script setup lang="ts">
import CrudTable from '@/components/CrudTable.vue'

const columns = [
  { prop: 'id', label: 'ID', width: 60 },
  { prop: 'name', label: '名称', width: 120 },
  { prop: 'type', label: '类型', width: 90 },
  { prop: 'price', label: '价格', width: 90 },
  { prop: 'duration_days', label: '天数', width: 80 },
  { prop: 'chat_limit', label: '对话限制', width: 90 },
  { prop: 'is_active', label: '启用', width: 70, type: 'switch' as const },
  { prop: 'sort_order', label: '排序', width: 70 },
]

const formFields = [
  { key: 'name', label: '名称', required: true },
  { key: 'type', label: '类型', type: 'select', options: [{ label: '月度', value: 'monthly' }, { label: '年度', value: 'yearly' }, { label: '自定义', value: 'custom' }], required: true },
  { key: 'price', label: '价格', required: true },
  { key: 'duration_days', label: '天数', required: true },
  { key: 'chat_limit', label: '对话限制' },
  { key: 'description', label: '描述', type: 'textarea' },
  { key: 'is_active', label: '启用', type: 'switch' },
  { key: 'sort_order', label: '排序' },
]
</script>

<template>
  <CrudTable api-base="/admin/plans" :columns="columns" :form-fields="formFields" create-btn-label="添加套餐" />
</template>
