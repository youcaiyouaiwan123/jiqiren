<script setup lang="ts">
import CrudTable from '@/components/CrudTable.vue'

const columns = [
  { prop: 'id', label: 'ID', width: 60 },
  { prop: 'name', label: '名称', width: 150 },
  { prop: 'webhook_url', label: 'Webhook 地址' },
  { prop: 'is_active', label: '启用', width: 70, type: 'switch' as const },
]

const formFields = [
  { key: 'name', label: '名称', required: true },
  { key: 'webhook_url', label: 'Webhook URL', required: true },
  { key: 'is_active', label: '启用', type: 'switch' },
]


</script>

<template>
  <CrudTable api-base="/admin/wecom/config" :columns="columns" :form-fields="formFields" create-btn-label="添加企微配置" />
</template>
