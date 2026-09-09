import type { Paginated } from './delivery'

export type PaymentStatus = 'unpaid' | 'partial' | 'paid' | 'overdue'

export type InvoiceItem = {
  id: string
  description: string
  quantity: string
  rate: string
  amount: string
}

export type InvoiceSummary = {
  id: string
  hostel_id: string
  invoice_number: string
  billing_month: string
  period_start: string
  period_end: string
  total_quantity: string
  subtotal: string
  tax: string
  adjustments: string
  total_amount: string
  payment_status: PaymentStatus | string
  due_date: string
  source_document_id: string | null
  created_at: string
  updated_at: string
}

export type Invoice = InvoiceSummary & {
  items: InvoiceItem[]
}

export type InvoiceCreate = {
  hostel_id: string
  billing_month: string
}

export type PaginatedInvoices = Paginated<InvoiceSummary>
