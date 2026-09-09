import type { Paginated } from './delivery'

export type PaymentMethod = 'cash' | 'upi' | 'bank_transfer' | 'cheque' | 'other'

export type Payment = {
  id: string
  invoice_id: string
  hostel_id: string
  amount: string
  payment_date: string
  payment_method: PaymentMethod | string
  reference_number: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export type PaymentCreate = {
  invoice_id: string
  amount: string
  payment_date: string
  payment_method: PaymentMethod
  reference_number?: string | null
}

export type PaginatedPayments = Paginated<Payment>
