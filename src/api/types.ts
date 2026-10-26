export type UserRole = 'user';

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  role: UserRole;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string;
}

export interface PaginatedResponse<T = unknown> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
}

export interface MessageResponse {
  message: string;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  citations: Citation[];
}

export interface Citation {
  source: string;
  external_id: string;
  score: number;
}

export interface RAGQueryRequest {
  query: string;
  top_k?: number;
}

export interface RAGSearchResult {
  chunk_text: string;
  source: string;
  external_id: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface RAGSearchResponse {
  available: boolean;
  query?: string;
  reason?: string;
  results: RAGSearchResult[];
}

export interface RAGQueryResponse {
  available: boolean;
  answer: string;
  reason?: string;
  citations: Citation[];
}

export interface RAGStatus {
  available: boolean;
  embedding_available: boolean;
  chunks_indexed: number;
  ingested_sources: string[];
  failed_sources: { source: string; external_id: string; reason: string; timestamp: string }[];
}

export interface RAGIngestRequest {
  source: string;
  external_id: string;
  title: string;
  content: string;
  metadata?: Record<string, unknown>;
}

export interface CaptureStatus {
  available: boolean;
  running: boolean;
  interface: string | null;
  reason: string | null;
  packets_captured: number;
}

export interface InterfaceInfo {
  name: string;
  address: string;
}

export interface CaptureStatistics {
  available: boolean;
  running: boolean;
  interface: string | null;
  packets_captured: number;
  active_flows: number;
  flow_details: FlowStatistics[];
}

export interface FlowStatistics {
  source_ip: string;
  destination_ip: string;
  protocol: string;
  source_port: number | null;
  destination_port: number | null;
  started_at: string;
  ended_at: string | null;
  packet_count: number;
  byte_count: number;
  duration_seconds: number;
}

export interface CapturePacketsResponse {
  available: boolean;
  running: boolean;
  packets_captured: number;
  reason: string | null;
}

export interface DetectionResultItem {
  id: string;
  label: string;
  confidence: number;
  model_version: string;
  detected_at: string;
}

export interface DetectionStatus {
  running: boolean;
  capture_running: boolean;
  model_available: boolean;
  detections_count: number;
}

export interface DetectionStatistics {
  total_detections: number;
}

export interface MetricValues {
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1?: number;
  roc_auc?: number;
}

export interface ModelStatus {
  model_available: boolean;
  model_version: string | null;
  training_timestamp: string | null;
  feature_schema_available: boolean;
  metrics_available: boolean;
  metrics: MetricValues | null;
  scaler_available: boolean;
  label_encoder_available: boolean;
}

export interface ModelMetrics {
  available: boolean;
  reason?: string;
  metrics?: MetricValues;
}

export interface ExplanationResponse {
  method: string;
  values: Record<string, number>;
}

export interface AlertRead {
  id: string;
  title: string;
  severity: string;
  status: string;
  description: string;
  acknowledged_by: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface ThreatIntelStatus {
  available: boolean;
  documents: number;
  rag_status: RAGStatus;
}

export interface ThreatIntelItem {
  id: string;
  title: string;
  content: string;
  source: string;
}

export interface QuantumStatus {
  kyber_available: boolean;
  kyber_variant: string;
  aes_gcm_available: boolean;
}

export interface QuantumKeygenResult {
  available: boolean;
  public_key: string | null;
  private_key_handle: string | null;
  reason: string | null;
}

export interface QuantumTestResult {
  available: boolean;
  keygen?: string;
  encapsulation?: string;
  decapsulation?: string;
  shared_secret_verified?: boolean;
  reason?: string;
}

export interface SystemStatus {
  api: boolean;
  database_configured: boolean;
  redis_configured: boolean;
  model_directory: string;
}

export interface HealthStatus {
  status: string;
  database: boolean;
}

export interface AssistantHistoryItem {
  id: string;
  title: string;
  created_at: string;
}

export type WsConnectionState = 'connected' | 'reconnecting' | 'disconnected';

export interface WsEvent {
  event: string;
  data: Record<string, unknown>;
}
