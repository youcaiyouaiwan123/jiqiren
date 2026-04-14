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
