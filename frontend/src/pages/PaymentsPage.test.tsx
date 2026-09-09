import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { PaymentsPage } from './PaymentsPage'

const invoice = {
  id: 'inv-1',
  hostel_id: 'h1',
  invoice_number: 'INV-202607-0001',
  billing_month: '2026-07',
  period_start: '2026-07-01',
  period_end: '2026-07-31',
  total_quantity: '22.750',
  subtotal: '1035.13',
  tax: '0.00',
  adjustments: '0.00',
  total_amount: '1035.13',
  payment_status: 'unpaid',
  due_date: '2026-08-10',
  source_document_id: null,
  created_at: '2026-08-01T00:00:00Z',
  updated_at: '2026-08-01T00:00:00Z',
}

const payment = {
  id: 'pay-1',
  invoice_id: 'inv-1',
  hostel_id: 'h1',
  amount: '1035.13',
  payment_date: '2026-08-02',
  payment_method: 'upi',
  reference_number: 'UPI-1',
  notes: null,
  created_at: '2026-08-02T00:00:00Z',
  updated_at: '2026-08-02T00:00:00Z',
}

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <PaymentsPage />
    </QueryClientProvider>,
  )
}

describe('PaymentsPage', () => {
  beforeEach(() => {
    let paid = false
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.includes('/api/v1/payments') && init?.method === 'POST') {
          paid = true
          return jsonResponse(payment, 201)
        }
        if (url.includes('/api/v1/payments')) {
          return jsonResponse({
            items: paid ? [payment] : [],
            page: 1,
            page_size: 100,
            total: paid ? 1 : 0,
          })
        }
        if (url.includes('/api/v1/invoices')) {
          return jsonResponse({
            items: [{ ...invoice, payment_status: paid ? 'paid' : 'unpaid' }],
            page: 1,
            page_size: 100,
            total: 1,
          })
        }
        return jsonResponse({}, 404)
      }),
    )
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('records a payment and shows the updated invoice status', async () => {
    const user = userEvent.setup()
    renderPage()
    expect(await screen.findByText('No payments recorded yet.')).toBeInTheDocument()
    expect(screen.getByLabelText('Reference')).toHaveAttribute('maxLength', '80')
    await screen.findByRole('option', { name: /INV-202607-0001 · ₹1035.13 · unpaid/ })
    await user.selectOptions(screen.getByLabelText('Invoice'), 'inv-1')
    fireEvent.change(screen.getByLabelText('Amount (₹)'), { target: { value: '1035.13' } })
    fireEvent.change(screen.getByLabelText('Payment date'), { target: { value: '2026-08-02' } })
    await user.click(screen.getByRole('button', { name: 'Save payment' }))
    expect(await screen.findByText(/INV-202607-0001 · status paid/)).toBeInTheDocument()
  })
})
