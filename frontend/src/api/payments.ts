import { apiGet, apiPost } from './client'
import { withQuery } from './errors'
import type { PaginatedPayments, Payment, PaymentCreate } from '../types/payment'

export function listPayments(
  filters: { hostel_id?: string; invoice_id?: string; from?: string; to?: string } = {},
  signal?: AbortSignal,
): Promise<PaginatedPayments> {
  return apiGet(
    withQuery('/api/v1/payments', {
      page: '1',
      page_size: '100',
      hostel_id: filters.hostel_id,
      invoice_id: filters.invoice_id,
      from: filters.from,
      to: filters.to,
    }),
    signal,
  )
}

export function createPayment(payload: PaymentCreate): Promise<Payment> {
  return apiPost<Payment>('/api/v1/payments', payload)
}
