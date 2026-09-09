import { apiGet, apiPost } from './client'
import { withQuery } from './errors'
import type { Invoice, InvoiceCreate, PaginatedInvoices } from '../types/invoice'

export function listInvoices(
  filters: { hostel_id?: string; billing_month?: string; payment_status?: string } = {},
  signal?: AbortSignal,
): Promise<PaginatedInvoices> {
  return apiGet(
    withQuery('/api/v1/invoices', {
      page: '1',
      page_size: '100',
      hostel_id: filters.hostel_id,
      billing_month: filters.billing_month,
      payment_status: filters.payment_status,
    }),
    signal,
  )
}

export function getInvoice(id: string, signal?: AbortSignal): Promise<Invoice> {
  return apiGet<Invoice>(`/api/v1/invoices/${id}`, signal)
}

export function createInvoice(payload: InvoiceCreate): Promise<Invoice> {
  return apiPost<Invoice>('/api/v1/invoices', payload)
}
