import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { DashboardPage } from './DashboardPage'

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
      <DashboardPage />
    </QueryClientProvider>,
  )
}

describe('DashboardPage', () => {
  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('shows KPI cards from the dashboard API', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse({
          as_of_date: '2026-09-10',
          timezone: 'Asia/Kolkata',
          currency_code: 'INR',
          active_hostel_count: 2,
          todays_supply: '20.000',
          revenue: '910.00',
          revenue_month: '2026-09',
          revenue_definition: 'paid invoice totals',
          pending_payments: '45.50',
          pending_definition: 'remaining balances',
        }),
      ),
    )
    renderPage()
    expect(await screen.findByText('Active hostels')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('20.000 L')).toBeInTheDocument()
    expect(screen.getByText('₹910.00')).toBeInTheDocument()
    expect(screen.getByText('₹45.50')).toBeInTheDocument()
    expect(screen.getByText(/Asia\/Kolkata/)).toBeInTheDocument()
  })

  it('shows an empty state when every total is zero', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse({
          as_of_date: '2026-09-10',
          timezone: 'Asia/Kolkata',
          currency_code: 'INR',
          active_hostel_count: 0,
          todays_supply: '0.000',
          revenue: '0.00',
          revenue_month: '2026-09',
          revenue_definition: 'paid invoice totals',
          pending_payments: '0.00',
          pending_definition: 'remaining balances',
        }),
      ),
    )
    renderPage()
    expect(
      await screen.findByText(/No billed activity yet/),
    ).toBeInTheDocument()
  })

  it('shows an error when the dashboard API fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
    renderPage()
    expect(
      await screen.findByText(/Could not load dashboard totals/),
    ).toBeInTheDocument()
  })
})
