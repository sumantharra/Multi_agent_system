import { apiDelete, apiGet, apiPost, apiPut } from './client'
import type { Hostel, HostelCreate, PaginatedHostels } from '../types/hostel'

export function listHostels(signal?: AbortSignal): Promise<PaginatedHostels> {
  return apiGet<PaginatedHostels>('/api/v1/hostels?page=1&page_size=100', signal)
}

export function createHostel(payload: HostelCreate): Promise<Hostel> {
  return apiPost<Hostel>('/api/v1/hostels', payload)
}

export function updateHostel(id: string, payload: Partial<HostelCreate> & { active?: boolean }): Promise<Hostel> {
  return apiPut<Hostel>(`/api/v1/hostels/${id}`, payload)
}

export function deactivateHostel(id: string): Promise<Hostel> {
  return apiDelete<Hostel>(`/api/v1/hostels/${id}`)
}
