/**
 * Central API client.
 * Authentication headers, base URL configuration, and error handling
 * will be added in Phase 2.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api/v1'

export const apiClient = {
  baseURL: API_BASE_URL,
  
  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`)
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    return response.json() as Promise<T>
  },
}

export type { }
