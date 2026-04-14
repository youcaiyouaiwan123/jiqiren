export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
  request_id: string
}

export interface PageData<T = unknown> {
  list: T[]
  total: number
  page: number
  page_size: number
}

export interface UserInfo {
  id: number
  nickname: string
  phone: string | null
  email: string | null
  avatar_url: string | null
  free_chats_left: number
  subscribe_plan: string
  subscribe_expire: string | null
  status: string
  created_at: string | null
}

export interface LoginResult {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: UserInfo
}

export interface AdminLoginResult {
  access_token: string
  token_type: string
  expires_in: number
  admin: { id: number; username: string; role: string }
}

export interface Conversation {
  id: number
  title: string | null
  message_count: number
  last_message_at: string | null
  created_at: string | null
  updated_at: string | null
}

export interface PlanDisplayConfig {
  badge_text?: string
  summary?: string
  original_price?: number | string
  button_text?: string
  feature_points?: string[]
  is_recommended?: boolean
  cta_url?: string
}

export interface SubscribePlan {
  id: number
  name: string
  type: 'monthly' | 'yearly' | 'custom'
  price: number | string
  duration_days: number
  chat_limit: number
  description: string | null
  display_config?: PlanDisplayConfig | null
  is_active: number
  sort_order: number
  created_at: string | null
  updated_at: string | null
}

export interface PaymentChannelOption {
  id: number
  channel: 'wechat' | 'alipay' | string
  display_name: string
  description: string
  button_label: string
  qrcode_url: string
  pay_tips: string
  checkout_url: string
}

export interface SubscribeCatalogData {
  current: Pick<UserInfo, 'subscribe_plan' | 'subscribe_expire' | 'free_chats_left'>
  plans: SubscribePlan[]
  channels: PaymentChannelOption[]
}

export interface SubscribeOrder {
  id: number
  order_no: string | null
  user_id?: number
  nickname?: string | null
  phone?: string | null
  email?: string | null
  type: 'subscribe' | 'redeem'
  plan: 'monthly' | 'yearly' | null
  plan_id: number | null
  plan_name?: string | null
  channel: string | null
  amount: number | string | null
  status: 'pending' | 'success' | 'failed'
  remark: string | null
  paid_at: string | null
  created_at: string | null
  updated_at: string | null
}

export interface KnowledgeDoc {
  title: string
  source: string
  score: number
  snippet: string
}

export interface RetrievalInfo {
  enabled?: boolean
  status: 'disabled' | 'success' | 'miss' | 'failed'
  mode?: 'vector' | 'keyword_fallback'
  provider?: string
  model?: string
  base_url?: string
  top_k?: number
  min_score?: number
  message?: string
  error?: string
  docs?: KnowledgeDoc[]
}

export interface ChatImage {
  url: string
  filename?: string
}

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  images: ChatImage[]
  docs: KnowledgeDoc[]
  retrieval?: RetrievalInfo | null
  created_at: string | null
}

export interface ChatDoneData {
  conversation_id: number
  user_message_id: number
  assistant_message_id: number
  text: string
  images: ChatImage[]
  docs: KnowledgeDoc[]
  retrieval?: RetrievalInfo | null
  usage: { model: string; input_tokens: number; output_tokens: number; cost_usd: number }
  quota: { free_chats_left: number; subscribe_plan: string; subscribe_expire: string | null }
}

export interface OverviewData {
  user_total: number
  user_today: number
  active_users_today: number
  conversation_total: number
  conversation_today: number
  message_total: number
  message_today: number
  token_input_total: number
  token_output_total: number
  cost_usd_total: number
  cost_usd_today: number
}
