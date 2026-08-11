import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { StatusPage } from './StatusPage'

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <StatusPage />
    </QueryClientProvider>,
  )
}

describe('StatusPage', () => {
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('shows a successful backend connection', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          status: 'ok',
          service: 'milk-supply-api',
          environment: 'development',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )

    renderPage()

    expect(screen.getByText('Checking backend connection…')).toBeInTheDocument()
    expect(await screen.findByText('Backend connected')).toBeInTheDocument()
    expect(screen.getByText('milk-supply-api · development')).toBeInTheDocument()
  })

  it('shows a clear error when the backend is unavailable', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Connection refused'))

    renderPage()

    expect(await screen.findByText('Backend unavailable')).toBeInTheDocument()
  })
})
