import { apiGet } from './client'
import type { DashboardSummary } from '../types/dashboard'

export function getDashboard(signal?: AbortSignal): Promise<DashboardSummary> {
  return apiGet<DashboardSummary>('/api/v1/dashboard', signal)
}
