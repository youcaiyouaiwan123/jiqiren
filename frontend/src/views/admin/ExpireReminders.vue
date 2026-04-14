<script setup lang="ts">
import CrudTable from '@/components/CrudTable.vue'

const columns = [
  { prop: 'id', label: 'ID', width: 60 },
  { prop: 'days_before', label: '提前天数', width: 100 },
  { prop: 'channel', label: '渠道', width: 90 },
  { prop: 'template', label: '模板内容' },
  { prop: 'is_active', label: '启用', width: 70, type: 'switch' as const },
]

const formFields = [
  { key: 'days_before', label: '提前天数', required: true },
  { key: 'channel', label: '渠道', type: 'select', options: [{ label: '站内', value: 'site' }, { label: '短信', value: 'sms' }, { label: '邮件', value: 'email' }], required: true },
  { key: 'template', label: '模板', type: 'textarea', required: true },
  { key: 'is_active', label: '启用', type: 'switch' },
]
</script>

<template>
  <CrudTable api-base="/admin/expire-reminders" :columns="columns" :form-fields="formFields" create-btn-label="添加提醒规则" />
</template>
