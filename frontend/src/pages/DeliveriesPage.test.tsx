import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { DeliveriesPage } from './DeliveriesPage'

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

const delivery = {
  id: 'd1',
  hostel_id: 'h1',
  delivery_date: '2026-07-01',
  morning_quantity: '12.500',
  evening_quantity: '10.250',
  total_quantity: '22.750',
  rate_per_liter: '45.50',
  notes: null,
  created_by: null,
  created_at: '2026-07-01T00:00:00Z',
  updated_at: '2026-07-01T00:00:00Z',
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
      <DeliveriesPage />
    </QueryClientProvider>,
  )
}

describe('DeliveriesPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.includes('/api/v1/hostels')) {
          return jsonResponse({ items: [hostel], page: 1, page_size: 100, total: 1 })
        }
        if (url.includes('/api/v1/deliveries') && init?.method === 'POST') {
          const payload = JSON.parse(String(init.body)) as Record<string, unknown>
          expect(payload).not.toHaveProperty('total_quantity')
          return jsonResponse(
            {
              error: {
                message: 'Delivery already exists for this hostel and date',
                details: [{ field: 'delivery_date', message: 'already exists' }],
              },
            },
            409,
          )
        }
        if (url.includes('/api/v1/deliveries')) {
          return jsonResponse({ items: [delivery], page: 1, page_size: 100, total: 1 })
        }
        return jsonResponse({}, 404)
      }),
    )
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('shows a computed total and lists deliveries', async () => {
    renderPage()
    expect(await screen.findByText(/Sai Hostel \(sai-01\) · 2026-07-01/)).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Morning quantity (L)'), { target: { value: '12.5' } })
    fireEvent.change(screen.getByLabelText('Evening quantity (L)'), { target: { value: '10.25' } })
    expect(screen.getByText('22.750 L')).toBeInTheDocument()
  })

  it('shows the server conflict for a duplicate hostel and date', async () => {
    const user = userEvent.setup()
    renderPage()
    await screen.findAllByRole('option', { name: 'Sai Hostel (sai-01)' })
    await user.selectOptions(screen.getAllByLabelText('Hostel')[0], 'h1')
    fireEvent.change(screen.getByLabelText('Date'), { target: { value: '2026-07-01' } })
    fireEvent.change(screen.getByLabelText('Morning quantity (L)'), { target: { value: '5' } })
    fireEvent.change(screen.getByLabelText('Evening quantity (L)'), { target: { value: '5' } })
    await user.click(screen.getByRole('button', { name: 'Save delivery' }))
    expect(
      await screen.findByText('Delivery already exists for this hostel and date'),
    ).toBeInTheDocument()
  })
})

describe('DeliveriesPage empty list', () => {
  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('says there are no deliveries yet when filters are unused', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input)
        if (url.includes('/api/v1/hostels')) {
          return jsonResponse({ items: [hostel], page: 1, page_size: 100, total: 1 })
        }
        if (url.includes('/api/v1/deliveries')) {
          return jsonResponse({ items: [], page: 1, page_size: 100, total: 0 })
        }
        return jsonResponse({}, 404)
      }),
    )
    renderPage()
    expect(await screen.findByText('No deliveries yet. Add one above.')).toBeInTheDocument()
  })
})
