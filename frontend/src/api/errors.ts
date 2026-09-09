import { ApiError } from './client'

type ErrorBody = {
  error?: {
    message?: string
    details?: { field?: string | null; message?: string }[]
  }
}

export function apiErrorMessage(error: unknown, fallback: string): string {
  if (!(error instanceof ApiError)) {
    return fallback
  }
  const body = error.body as ErrorBody | null
  if (body?.error?.message) {
    return body.error.message
  }
  const detail = body?.error?.details?.[0]
  if (detail?.message) {
    return detail.field ? `${detail.field}: ${detail.message}` : detail.message
  }
  return fallback
}

export function withQuery(path: string, params: Record<string, string | undefined>): string {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value) {
      query.set(key, value)
    }
  }
  const serialized = query.toString()
  return serialized ? `${path}?${serialized}` : path
}
