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

export type AssistantStatus =
  | 'ok'
  | 'truncated'
  | 'insufficient_evidence'
  | 'empty_query'
  | 'llm_not_configured'
  | 'rag_unavailable'
  | 'llm_timeout'
  | 'llm_unavailable'
  | 'llm_model_missing'
  | 'llm_error'
  | 'llm_malformed_response'
  | 'llm_empty_response';

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  citations: Citation[];
  status: AssistantStatus;
}

export interface Citation {
  index?: number;
  document_id?: string;
  source: string;
  external_id: string;
  score: number;
  matched_identifiers?: string[];
}

export interface RAGQueryRequest {
  query: string;
  top_k?: number;
}

export interface RAGSearchResult {
  document_id: string;
  chunk_text: string;
  source: string;
  external_id: string;
  score: number;
  lexical_score: number;
  matched_identifiers: string[];
  metadata: Record<string, unknown>;
}

export interface RAGSearchResponse {
  available: boolean;
  query?: string;
  reason?: string;
  retrieval_ms?: number;
  results: RAGSearchResult[];
}

export interface RAGQueryResponse {
  status: AssistantStatus;
  answer: string;
  citations: Citation[];
  retrieval_ms: number | null;
  generation_ms: number | null;
  model: string | null;
}

export interface LLMHealth {
  reachable: boolean;
  model_available: boolean;
  installed_models: string[];
  error: string | null;
  base_url: string;
  model: string;
}

export interface RAGStatus {
  available: boolean;
  embedding_available: boolean;
  embedding_loaded: boolean;
  embedding_model: string;
  chunks_indexed: number;
  min_similarity: number;
  last_retrieval_ms: number | null;
  documents: number;
  chunks_stored: number;
  chunks_with_current_embedding_model: number;
  last_ingested_at: string | null;
  ingested_sources: string[];
  llm?: LLMHealth;
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
  source_ip: string | null;
  destination_ip: string | null;
  protocol: string | null;
  source_port: number | null;
  destination_port: number | null;
  severity: string | null;
  classification: string | null;
  anomaly_score: number | null;
}

export interface DetectionStatus {
  running: boolean;
  capture_running: boolean;
  model_available: boolean;
  detections_count: number;
}

export interface DetectionStatistics {
  total_detections: number;
  by_label: Record<string, number>;
  by_severity: Record<string, number>;
  by_classification: Record<string, number>;
}

export interface DetectionHistoryBucket {
  timestamp: string;
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface DetectionHistory {
  hours: number;
  buckets: DetectionHistoryBucket[];
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
