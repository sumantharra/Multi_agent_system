import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { InvoicesPage } from './InvoicesPage'

const hostel = {
  id: 'h1',
  name: 'Sai Hostel',
  code: 'sai-01',
  address: null,
  contact_name: null,
  phone: null,
  default_rate_per_liter: '45.50',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

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
      <InvoicesPage />
    </QueryClientProvider>,
  )
}

describe('InvoicesPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.includes('/api/v1/hostels')) {
          return jsonResponse({ items: [hostel], page: 1, page_size: 100, total: 1 })
        }
        if (url.includes('/api/v1/invoices') && init?.method === 'POST') {
          const payload = JSON.parse(String(init.body)) as { billing_month?: string }
          if (payload.billing_month === '2026-08') {
            return jsonResponse(
              {
                error: {
                  message: 'No deliveries found for this hostel and billing month',
                  details: [{ field: 'billing_month', message: 'no deliveries' }],
                },
              },
              422,
            )
          }
          return jsonResponse(
            {
              error: {
                message: 'Invoice already exists for this hostel and billing month',
                details: [{ field: 'billing_month', message: 'already exists' }],
              },
            },
            409,
          )
        }
        if (url.includes('/api/v1/invoices/inv-1')) {
          return jsonResponse({
            ...invoice,
            items: [
              {
                id: 'item-1',
                description: 'Milk supply July',
                quantity: '22.750',
                rate: '45.50',
                amount: '1035.13',
              },
            ],
          })
        }
        if (url.includes('/api/v1/invoices')) {
          return jsonResponse({ items: [invoice], page: 1, page_size: 100, total: 1 })
        }
        return jsonResponse({}, 404)
      }),
    )
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('lists invoices and opens line-item detail', async () => {
    const user = userEvent.setup()
    renderPage()
    expect(await screen.findByText('INV-202607-0001')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'View' }))
    expect(await screen.findByText(/Milk supply July/)).toBeInTheDocument()
    expect(screen.getByText(/status unpaid/)).toBeInTheDocument()
    expect(screen.getByText(/Period 2026-07-01 – 2026-07-31 · due 2026-08-10/)).toBeInTheDocument()
  })

  it('shows the server conflict for a duplicate billing month', async () => {
    const user = userEvent.setup()
    renderPage()
    await screen.findAllByRole('option', { name: 'Sai Hostel (sai-01)' })
    await user.selectOptions(screen.getAllByLabelText('Hostel')[0], 'h1')
    fireEvent.change(screen.getByLabelText('Billing month'), { target: { value: '2026-07' } })
    await user.click(screen.getByRole('button', { name: 'Create invoice' }))
    expect(
      await screen.findByText('Invoice already exists for this hostel and billing month'),
    ).toBeInTheDocument()
  })

  it('shows the server error when the month has no deliveries', async () => {
    const user = userEvent.setup()
    renderPage()
    await screen.findAllByRole('option', { name: 'Sai Hostel (sai-01)' })
    await user.selectOptions(screen.getAllByLabelText('Hostel')[0], 'h1')
    fireEvent.change(screen.getByLabelText('Billing month'), { target: { value: '2026-08' } })
    await user.click(screen.getByRole('button', { name: 'Create invoice' }))
    expect(
      await screen.findByText('No deliveries found for this hostel and billing month'),
    ).toBeInTheDocument()
  })
})
