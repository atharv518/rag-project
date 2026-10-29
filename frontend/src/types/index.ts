/**
 * Shared TypeScript types for the RAG project.
 * Feature-specific types live in their respective feature directories.
 */

export interface ApiError {
  error: {
    code: string
    message: string
    request_id?: string
  }
}

export interface HealthStatus {
  status: 'ok' | 'degraded'
  database: 'ok' | 'error'
  version: string
}
