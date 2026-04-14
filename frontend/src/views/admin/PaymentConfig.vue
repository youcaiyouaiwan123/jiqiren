<script setup lang="ts">
import CrudTable from '@/components/CrudTable.vue'

const columns = [
  { prop: 'id', label: 'ID', width: 60 },
  { prop: 'channel', label: '渠道', width: 100 },
  { prop: 'merchant_id', label: '商户号', width: 180 },
  { prop: 'notify_url', label: '回调地址' },
  { prop: 'is_active', label: '启用', width: 70, type: 'switch' as const },
]

const formFields = [
  { key: 'channel', label: '渠道', type: 'select', options: [{ label: '微信', value: 'wechat' }, { label: '支付宝', value: 'alipay' }], required: true },
  { key: 'merchant_id', label: '商户号' },
  { key: 'api_key', label: 'API Key', type: 'password' },
  { key: 'api_secret', label: 'API Secret', type: 'password' },
  { key: 'notify_url', label: '回调地址' },
  { key: 'is_active', label: '启用', type: 'switch' },
]
</script>

<template>
  <CrudTable api-base="/admin/payment/config" :columns="columns" :form-fields="formFields" create-btn-label="添加支付渠道" />
</template>
