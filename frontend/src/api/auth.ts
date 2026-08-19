import { apiGet, apiPost } from './client'
import type { AuthUser, BrandInfo, TokenResponse } from '../types/auth'

export function getBrand(): Promise<BrandInfo> {
  return apiGet<BrandInfo>('/api/v1/auth/brand')
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>('/api/v1/auth/login', { email, password })
}

export function logout(): Promise<null> {
  return apiPost<null>('/api/v1/auth/logout')
}

export function getMe(signal?: AbortSignal): Promise<AuthUser> {
  return apiGet<AuthUser>('/api/v1/auth/me', signal)
}
