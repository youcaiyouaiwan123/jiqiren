<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { AlarmClock, ArrowDown, ArrowRight, Bell, ChatDotRound, CircleClose, Cpu, DataAnalysis, Document, EditPen, Key, Medal, Money, Setting, Ticket, TrendCharts, User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const adminStore = useAdminStore()
const collapsed = ref(false)

type MenuLeaf = { path: string; label: string; icon: any }
type MenuGroup = { key: string; label: string; icon: any; children: MenuLeaf[] }
type MenuEntry = MenuLeaf | MenuGroup

const menuItems: MenuEntry[] = [
  { path: '/admin/dashboard', label: '数据分析', icon: DataAnalysis },
  {
    key: 'users',
    label: '用户',
    icon: User,
    children: [
      { path: '/admin/users', label: '用户管理', icon: User },
      { path: '/admin/invite-codes', label: '邀请码', icon: Key },
      { path: '/admin/redeem-codes', label: '兑换码', icon: Ticket },
    ],
  },
  {
    key: 'ai',
    label: 'AI 配置',
    icon: Cpu,
    children: [
      { path: '/admin/llm', label: '大模型配置', icon: Cpu },
      { path: '/admin/ai-config', label: 'AI 配置', icon: Setting },
      { path: '/admin/knowledge', label: '知识源配置', icon: Document },
      { path: '/admin/knowledge-files', label: '知识库文档', icon: EditPen },
    ],
  },
  {
    key: 'billing',
    label: '商业化',
    icon: Money,
    children: [
      { path: '/admin/plans', label: '套餐管理', icon: Medal },
      { path: '/admin/payment-orders', label: '订单管理', icon: Ticket },
      { path: '/admin/payment', label: '支付设置', icon: Money },
      { path: '/admin/token-usage', label: 'Token 计费', icon: TrendCharts },
      { path: '/admin/expire-reminders', label: '到期提醒', icon: AlarmClock },
    ],
  },
  {
    key: 'ops',
    label: '运营',
    icon: Setting,
    children: [
      { path: '/admin/announcements', label: '公告管理', icon: Bell },
      { path: '/admin/banned-words', label: '禁用词', icon: CircleClose },
      { path: '/admin/register', label: '注册设置', icon: EditPen },
      { path: '/admin/feishu', label: '飞书配置', icon: Document },
      { path: '/admin/wecom', label: '企微配置', icon: ChatDotRound },
    ],
  },
]

function isGroup(item: MenuEntry): item is MenuGroup {
  return (item as MenuGroup).children !== undefined
}

const activePath = computed(() => route.path)

// 默认展开当前路由所在的分组
const expanded = ref<Record<string, boolean>>(
  menuItems.reduce((acc: Record<string, boolean>, item) => {
    if (isGroup(item) && item.children.some(c => c.path === route.path)) {
      acc[item.key] = true
    }
    return acc
  }, {})
)

function toggleGroup(key: string) {
  expanded.value[key] = !expanded.value[key]
}

const currentLabel = computed(() => {
  for (const item of menuItems) {
    if (isGroup(item)) {
      const hit = item.children.find(c => c.path === activePath.value)
      if (hit) return hit.label
    } else if (item.path === activePath.value) {
      return item.label
    }
  }
  return '管理后台'
})

function navigate(path: string) {
  router.push(path)
}

function handleLogout() {
  adminStore.logout()
  router.push('/admin/login')
}
</script>

<template>
  <div class="flex h-screen bg-[#f5f7fa]">
    <aside class="admin-sidebar flex shrink-0 flex-col overflow-hidden text-slate-300 transition-all duration-200" :class="collapsed ? 'w-20' : 'w-60'">
      <div class="flex h-14 shrink-0 items-center border-b border-white/10" :class="collapsed ? 'justify-center px-0' : 'gap-3 px-4'">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-500/20 text-blue-200 ring-1 ring-white/10">
          <el-icon :size="18"><Setting /></el-icon>
        </div>
        <div v-if="!collapsed" class="min-w-0">
          <div class="truncate text-sm font-semibold text-white">管理后台</div>
          <div class="mt-0.5 text-[10px] text-slate-400">系统控制台</div>
        </div>
      </div>
      <nav class="admin-sidebar-nav flex-1 overflow-y-auto px-2 py-3">
        <template v-for="item in menuItems" :key="isGroup(item) ? item.key : item.path">
          <!-- 单项 -->
          <div
            v-if="!isGroup(item)"
            class="admin-menu-item group flex cursor-pointer items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors duration-150"
            :class="activePath === item.path ? 'is-active bg-blue-500/15 text-white font-medium' : 'text-slate-400 hover:bg-white/5 hover:text-white'"
            @click="navigate(item.path)"
          >
            <span class="admin-menu-icon shrink-0">
              <el-icon :size="16"><component :is="item.icon" /></el-icon>
            </span>
            <span v-if="!collapsed" class="min-w-0 flex-1 truncate">{{ item.label }}</span>
          </div>
          <!-- 分组 -->
          <div v-else>
            <div
              class="admin-menu-item group flex cursor-pointer items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors duration-150 text-slate-400 hover:bg-white/5 hover:text-white"
              @click="toggleGroup(item.key)"
            >
              <span class="admin-menu-icon shrink-0">
                <el-icon :size="16"><component :is="item.icon" /></el-icon>
              </span>
              <span v-if="!collapsed" class="min-w-0 flex-1 truncate">{{ item.label }}</span>
              <el-icon v-if="!collapsed" :size="12" class="text-slate-500 transition-transform" :class="expanded[item.key] ? 'rotate-0' : '-rotate-90'">
                <ArrowDown />
              </el-icon>
            </div>
            <div v-show="expanded[item.key] && !collapsed" class="ml-2.5 mb-1 border-l border-white/10 pl-2">
              <div
                v-for="child in item.children"
                :key="child.path"
                class="admin-menu-item admin-menu-child flex cursor-pointer items-center gap-2 rounded-md px-2.5 py-1.5 text-[13px] transition-colors duration-150"
                :class="activePath === child.path ? 'is-active bg-blue-500/15 text-white font-medium' : 'text-slate-500 hover:bg-white/5 hover:text-white'"
                @click="navigate(child.path)"
              >
                <span class="admin-menu-dot"></span>
                <span class="min-w-0 flex-1 truncate">{{ child.label }}</span>
              </div>
            </div>
            <!-- 折叠状态下显示子项图标 -->
            <div v-if="collapsed" class="flex flex-col items-center gap-1 mb-1">
              <div
                v-for="child in item.children"
                :key="child.path"
                class="admin-menu-item flex cursor-pointer items-center justify-center rounded-md p-1.5 text-xs transition-colors duration-150"
                :class="activePath === child.path ? 'is-active bg-blue-500/15 text-white' : 'text-slate-500 hover:bg-white/5 hover:text-slate-300'"
                @click="navigate(child.path)"
                :title="child.label"
              >
                <el-icon :size="13"><component :is="child.icon" /></el-icon>
              </div>
            </div>
          </div>
        </template>
      </nav>
      <div class="shrink-0 border-t border-white/10 p-2.5">
        <button class="admin-collapse-btn w-full rounded-md border border-white/10 bg-white/5 py-2 text-xs font-medium text-slate-400 transition hover:bg-white/10 hover:text-white" @click="collapsed = !collapsed">
          {{ collapsed ? '展开' : '收起导航' }}
        </button>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header class="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-5">
        <h1 class="text-sm font-semibold text-slate-800">
          {{ currentLabel }}
        </h1>
        <div class="flex items-center gap-2">
          <span class="cursor-pointer text-xs text-slate-500 hover:text-slate-900 transition-colors" @click="router.push('/admin/profile')">{{ adminStore.admin?.username || 'admin' }}</span>
          <el-button size="small" text @click="router.push('/admin/profile')">个人中心</el-button>
          <el-button size="small" text type="danger" @click="handleLogout">退出</el-button>
        </div>
      </header>
      <main class="flex-1 overflow-y-auto bg-[#f5f7fa] p-5">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-sidebar {
  background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
}

.admin-sidebar-nav {
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.35) transparent;
}

.admin-sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.admin-sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.admin-sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.32);
  border-radius: 9999px;
}

.admin-sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.52);
}

.admin-menu-item {
  margin-bottom: 2px;
}

.admin-menu-child {
  margin-bottom: 1px;
}

.admin-menu-dot {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  background: rgba(148, 163, 184, 0.55);
  flex-shrink: 0;
}

.admin-menu-child.is-active .admin-menu-dot {
  background: #0f172a;
}

.admin-menu-icon {
  display: flex;
  height: 26px;
  width: 26px;
  align-items: center;
  justify-content: center;
  color: inherit;
  transition: color 0.15s ease;
}

.admin-menu-item:hover .admin-menu-icon {
  color: #0f172a;
}

.admin-menu-item.is-active .admin-menu-icon {
  color: #0f172a;
}

.admin-collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
