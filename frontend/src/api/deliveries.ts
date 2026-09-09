import { apiGet, apiPost } from './client'
import { withQuery } from './errors'
import type { Delivery, DeliveryCreate, Paginated } from '../types/delivery'

export function listDeliveries(
  filters: { hostel_id?: string; from?: string; to?: string } = {},
  signal?: AbortSignal,
): Promise<Paginated<Delivery>> {
  return apiGet(
    withQuery('/api/v1/deliveries', {
      page: '1',
      page_size: '100',
      hostel_id: filters.hostel_id,
      from: filters.from,
      to: filters.to,
    }),
    signal,
  )
}

export function createDelivery(payload: DeliveryCreate): Promise<Delivery> {
  return apiPost<Delivery>('/api/v1/deliveries', payload)
}
