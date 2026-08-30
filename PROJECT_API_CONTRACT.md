# Q-Sentinel API Contract

This document describes the contract between the frontend and backend API.

## Base URL

- Development: `http://localhost:8000`
- Set via `VITE_API_BASE_URL` environment variable

## Authentication

All authenticated endpoints require a `Bearer` token in the `Authorization` header.
Tokens are obtained from `/api/v1/auth/login` and refreshed via `/api/v1/auth/refresh`.

### Auth Endpoints

| Method | Path | Body | Response | Permission |
|--------|------|------|----------|------------|
| POST | `/api/v1/auth/register` | `{ email, password, full_name? }` | `UserRead` | Public |
| POST | `/api/v1/auth/login` | `{ email, password }` | `{ access_token, refresh_token, token_type }` | Public |
| POST | `/api/v1/auth/refresh` | `refresh_token` (text/plain) | `{ access_token, refresh_token, token_type }` | Public |
| POST | `/api/v1/auth/logout` | — | `{ message }` | Authenticated |
| GET | `/api/v1/auth/me` | — | `UserRead` | Authenticated |
| POST | `/api/v1/auth/forgot-password` | — | `{ message }` | Public (501) |
| POST | `/api/v1/auth/reset-password` | — | `{ message }` | Public (501) |

### UserRead

```typescript
{
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  role: 'admin' | 'analyst' | 'viewer';
}
```

## System Endpoints

| Method | Path | Response | Permission |
|--------|------|----------|------------|
| GET | `/health` | `{ status: 'ok'|'degraded', database: boolean }` | Public |
| GET | `/api/v1/system/status` | `{ api, database_configured, redis_configured, model_directory }` | Public |

## Capture Endpoints

| Method | Path | Query | Response | Permission |
|--------|------|-------|----------|------------|
| GET | `/api/v1/capture/interfaces` | — | `[{ name, address }]` | capture:view |
| GET | `/api/v1/capture/status` | — | `CaptureStatus` | capture:view |
| POST | `/api/v1/capture/start` | `?interface=` | `{ status, interface }` | capture:start |
| POST | `/api/v1/capture/stop` | — | `{ status }` | capture:stop |
| GET | `/api/v1/capture/statistics` | — | `CaptureStatistics` | capture:view |
| GET | `/api/v1/capture/packets` | — | `CapturePacketsResponse` | capture:view |

### CaptureStatus

```typescript
{
  available: boolean;
  running: boolean;
  interface: string | null;
  reason: string | null;
  packets_captured: number;
}
```

### CaptureStatistics

```typescript
{
  available: boolean;
  running: boolean;
  interface: string | null;
  packets_captured: number;
  active_flows: number;
  flow_details: FlowStatistics[];
}
```

### FlowStatistics

```typescript
{
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
```

## Detection Endpoints

| Method | Path | Query | Response | Permission |
|--------|------|-------|----------|------------|
| GET | `/api/v1/detection/status` | — | `DetectionStatus` | Authenticated |
| POST | `/api/v1/detection/start` | `?interface=` | `{ status, interface }` | capture:start |
| POST | `/api/v1/detection/stop` | — | `{ status }` | capture:stop |
| GET | `/api/v1/detection/results` | `?page=&page_size=` | `PaginatedResponse<DetectionResultItem>` | detection:view |
| GET | `/api/v1/detection/statistics` | — | `{ total_detections }` | detection:view |
| GET | `/api/v1/detection/model/status` | — | `ModelStatus` | Authenticated |
| GET | `/api/v1/detection/model/metrics` | — | `ModelMetrics` | Authenticated |
| GET | `/api/v1/detection/{id}/explanation` | — | `{ method, values }` | detection:view |

### DetectionStatus

```typescript
{
  running: boolean;
  capture_running: boolean;
  model_available: boolean;
  detections_count: number;
}
```

### DetectionResultItem

```typescript
{
  id: string;
  label: string;
  confidence: number;
  model_version: string;
  detected_at: string;
}
```

### ModelStatus

```typescript
{
  model_available: boolean;
  model_version: string | null;
  training_timestamp: string | null;
  feature_schema_available: boolean;
  metrics_available: boolean;
  metrics: { accuracy?, precision?, recall?, f1?, roc_auc? } | null;
  scaler_available: boolean;
  label_encoder_available: boolean;
}
```

## Alert Endpoints

| Method | Path | Query | Response | Permission |
|--------|------|-------|----------|------------|
| GET | `/api/v1/alerts` | `?page=&page_size=` | `PaginatedResponse<AlertRead>` | alerts:view |
| GET | `/api/v1/alerts/{id}` | — | `AlertRead` | alerts:view |
| POST | `/api/v1/alerts/{id}/acknowledge` | — | `AlertRead` | alerts:update |
| POST | `/api/v1/alerts/{id}/resolve` | — | `AlertRead` | alerts:update |
| POST | `/api/v1/alerts/{id}/reopen` | — | `AlertRead` | alerts:update |

### AlertRead

```typescript
{
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'acknowledged' | 'resolved';
  description: string;
  acknowledged_by: string | null;
  resolved_at: string | null;
  created_at: string;
}
```

## Quantum Endpoints

| Method | Path | Response | Permission |
|--------|------|----------|------------|
| GET | `/api/v1/quantum/status` | `QuantumStatus` | Authenticated |
| POST | `/api/v1/quantum/keygen` | `QuantumKeygenResult` | quantum:view |
| POST | `/api/v1/quantum/test` | `QuantumTestResult` | quantum:view |

### QuantumStatus

```typescript
{
  kyber_available: boolean;
  kyber_variant: string;
  aes_gcm_available: boolean;
}
```

### QuantumTestResult

```typescript
{
  available: boolean;
  keygen?: string;
  encapsulation?: string;
  decapsulation?: string;
  shared_secret_verified?: boolean;
  reason?: string;
}
```

## RAG / Threat Intelligence Endpoints

| Method | Path | Body | Response | Permission |
|--------|------|------|----------|------------|
| GET | `/api/v1/threat-intel` | — | `ThreatIntelStatus` | threatintel:view |
| GET | `/api/v1/threat-intel/{id}` | — | `ThreatIntelItem` | threatintel:view |
| GET | `/api/v1/rag/status` | — | `RAGStatus` | threatintel:view |
| POST | `/api/v1/rag/ingest` | `RAGIngestRequest` | `{ ingested, chunks_created, document_id }` | threatintel:view |
| POST | `/api/v1/rag/search` | `{ query, top_k? }` | `RAGSearchResponse` | threatintel:view |
| POST | `/api/v1/rag/query` | `{ query, top_k? }` | `RAGQueryResponse` | threatintel:view |

## AI Assistant Endpoints

| Method | Path | Body | Response | Permission |
|--------|------|------|----------|------------|
| POST | `/api/v1/assistant/chat` | `{ conversation_id?, message }` | `ChatResponse` | assistant:use |
| GET | `/api/v1/assistant/history` | — | `AssistantHistoryItem[]` | assistant:use |

## Reports Endpoints

| Method | Path | Response | Permission |
|--------|------|----------|------------|
| GET | `/api/v1/reports` | `PaginatedResponse` | reports:view |
| POST | `/api/v1/reports/generate` | — | reports:view (503) |

## WebSocket

- URL: `ws://host/api/v1/ws?token=<access_token>`
- Events: `packet_received`, `capture_started`, `capture_stopped`, `detection_created`, `alert_created`, `alert_updated`, `model_status`, `system_status`, `quantum_event`

## Roles and Permissions

| Permission | Admin | Analyst | Viewer |
|------------|-------|---------|--------|
| dashboard:view | Yes | Yes | Yes |
| capture:view | Yes | Yes | — |
| capture:start | Yes | Yes | — |
| capture:stop | Yes | Yes | — |
| detection:view | Yes | Yes | Yes |
| alerts:view | Yes | Yes | Yes |
| alerts:update | Yes | Yes | — |
| threatintel:view | Yes | Yes | Yes |
| assistant:use | Yes | Yes | — |
| reports:view | Yes | Yes | Yes |
| quantum:view | Yes | Yes | Yes |
| settings:view | Yes | Yes | Yes |
| settings:update | Yes | — | — |
| admin:manage | Yes | — | — |
