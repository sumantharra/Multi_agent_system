import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { HostelsPage } from './HostelsPage'

const hostel = {
  id: 'h1',
  name: 'Sai Hostel',
  code: 'sai-01',
  address: 'Main road',
  contact_name: 'Ravi',
  phone: '999',
  default_rate_per_liter: '45.50',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
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
      <HostelsPage />
    </QueryClientProvider>,
  )
}

describe('HostelsPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.includes('/api/v1/hostels/h1') && init?.method === 'PUT') {
          const payload = JSON.parse(String(init.body)) as { name: string }
          return jsonResponse({ ...hostel, name: payload.name })
        }
        if (url.includes('/api/v1/hostels')) {
          return jsonResponse({ items: [hostel], page: 1, page_size: 100, total: 1 })
        }
        return jsonResponse({}, 404)
      }),
    )
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('loads a hostel into the form for edit', async () => {
    const user = userEvent.setup()
    renderPage()
    expect(await screen.findByText(/Sai Hostel/)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Edit' }))
    expect(screen.getByRole('heading', { name: 'Edit hostel' })).toBeInTheDocument()
    expect(screen.getByLabelText('Name')).toHaveValue('Sai Hostel')
    expect(screen.getByLabelText('Code')).toHaveValue('sai-01')
    expect(screen.getByLabelText('Active')).toBeChecked()
    expect(screen.getByRole('button', { name: 'Save changes' })).toBeInTheDocument()
  })
})
