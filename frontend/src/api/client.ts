const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export class ApiError extends Error {
  status: number
  body: unknown

  constructor(status: number, body: unknown) {
    super(`API request failed with status ${status}`)
    this.status = status
    this.body = body
  }
}

type TokenGetter = () => string | null

let tokenGetter: TokenGetter = () => null

export function setAccessTokenGetter(getter: TokenGetter) {
  tokenGetter = getter
}

async function parseJson(response: Response): Promise<unknown> {
  const text = await response.text()
  if (!text) {
    return null
  }
  return JSON.parse(text) as unknown
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  headers.set('Accept', 'application/json')
  if (init?.body) {
    headers.set('Content-Type', 'application/json')
  }
  const token = tokenGetter()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: 'include',
  })

  const body = await parseJson(response)
  if (!response.ok) {
    throw new ApiError(response.status, body)
  }

  return body as T
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  return request<T>(path, { method: 'GET', signal })
}

export async function apiPost<T>(path: string, payload?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: payload === undefined ? undefined : JSON.stringify(payload),
  })
}

export async function apiPut<T>(path: string, payload: unknown): Promise<T> {
  return request<T>(path, { method: 'PUT', body: JSON.stringify(payload) })
}

export async function apiDelete<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'DELETE' })
}
