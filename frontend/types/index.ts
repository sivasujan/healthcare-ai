export interface ApiEnvelope<T = unknown> {
  success: boolean;
  message: string | null;
  data: T;
  errors?: Array<{ field: string; message: string }> | null;
  status_code?: number;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  phone?: string | null;
  role: string;
  is_admin: boolean;
  created_at: string;
}

export interface Profile extends User {
  age?: number | null;
  gender?: string | null;
  height_cm?: number | null;
  weight_kg?: number | null;
  blood_group?: string | null;
  medical_history?: string | null;
  allergies?: string | null;
  current_medications?: string | null;
  preferred_language: string;
  dark_mode: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface ChatSummary {
  id: number;
  title: string;
  agent: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  agent?: string | null;
  model?: string | null;
  created_at: string;
}

export interface ChatDetail extends ChatSummary {
  messages: ChatMessage[];
}

export interface ChatSendResponse {
  chat_id: number;
  message_id: number;
  agent: string;
  model: string;
  response: string;
  data: Record<string, unknown> | null;
  title: string;
}

export interface Condition {
  name: string;
  confidence: number;
  severity: string;
}

export interface SymptomAnalysisResult {
  possible_conditions: Condition[];
  overall_severity: string;
  recommendations: Array<{ title: string; detail: string }>;
  precautions: string[];
  doctor_specialty: string;
  doctor_reason: string;
  emergency_detected: boolean;
  emergency_instructions?: string[] | null;
  disclaimer: string;
  model: string;
}

export interface MedicineOut {
  id: number;
  name: string;
  generic_name?: string | null;
  category?: string | null;
  purpose?: string | null;
  uses?: string | null;
  dosage?: string | null;
  warnings?: string | null;
  side_effects?: string | null;
  interactions?: string | null;
  storage?: string | null;
  notes?: string | null;
  source: string;
  created_at: string;
}

export interface MedicineSearchResult {
  medicine?: MedicineOut | null;
  summary?: string | null;
  disclaimer: string;
  model: string;
}

export interface DoctorRecommendationResult {
  specialty: string;
  reason: string;
  consultation_type: string;
  urgency: string;
  preparation_tips: string[];
  nearby_hospitals: string[];
  disclaimer: string;
  model: string;
}

export interface EmergencyCheckResult {
  emergency_detected: boolean;
  severity: string;
  conditions: string[];
  instructions: string[];
  immediate_actions: string[];
  nearby_hospitals: string[];
  emergency_number: string;
  disclaimer: string;
  model: string;
}

export interface Appointment {
  id: number;
  title: string;
  doctor_name: string;
  specialty: string;
  hospital?: string | null;
  appointment_date: string;
  appointment_time: string;
  status: "scheduled" | "confirmed" | "cancelled" | "completed";
  notes?: string | null;
  created_at: string;
}

export interface AdminDashboardStats {
  total_users: number;
  total_chats: number;
  total_messages: number;
  total_appointments: number;
  active_appointments: number;
  total_searches: number;
  total_prompts: number;
  total_model_usage_rows: number;
  total_tokens: number;
  total_cost_usd: number;
}

export interface AdminChatLog {
  id: number;
  user_id: number;
  user_email?: string | null;
  title: string;
  agent: string;
  message_count: number;
  created_at: string;
}

export interface ModelUsageRow {
  id: number;
  model: string;
  tier?: string | null;
  agent?: string | null;
  total_tokens: number;
  cost_usd: number;
  success: number;
  created_at: string;
}

export interface PromptLogRow {
  id: number;
  agent?: string | null;
  model?: string | null;
  prompt: string;
  created_at: string;
}

export interface SystemLogRow {
  id: number;
  level: string;
  event: string;
  method?: string | null;
  path?: string | null;
  status_code?: number | null;
  response_time_ms?: number | null;
  message?: string | null;
  created_at: string;
}
