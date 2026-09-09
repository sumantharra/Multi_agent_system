import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { AppRoutes } from '../../routes/AppRoutes'
import type { AuthUser } from '../../types/auth'

const { authState } = vi.hoisted(() => {
  const state: {
    user: AuthUser | null
    token: string | null
    loading: boolean
    login: ReturnType<typeof vi.fn>
    logout: ReturnType<typeof vi.fn>
  } = {
    user: {
      id: 'user-1',
      email: 'admin@local.test',
      role: 'owner',
      active: true,
    },
    token: 'token',
    loading: false,
    login: vi.fn(),
    logout: vi.fn(async () => {
      state.user = null
      state.token = null
    }),
  }
  return { authState: state }
})

vi.mock('../../auth/AuthContext', () => ({
  useAuth: () => authState,
}))

function renderApp(path: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('AppShell', () => {
  beforeEach(() => {
    authState.user = {
      id: 'user-1',
      email: 'admin@local.test',
      role: 'owner',
      active: true,
    }
    authState.token = 'token'
    authState.loading = false
    authState.logout.mockClear()
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            status: 'ok',
            service: 'multi-agent-api',
            environment: 'development',
            items: [],
            page: 1,
            page_size: 20,
            total: 0,
            name: 'RR Vijaya Milk Agencies',
            domain: 'rrvijayamilkagencies.com',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      ),
    )
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('shows shared nav and email on hostels', async () => {
    renderApp('/hostels')

    expect(await screen.findByRole('navigation', { name: 'Main' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Hostels' })).toHaveAttribute('aria-current', 'page')
    expect(screen.getByText('admin@local.test')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Log out' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Hostels' })).toBeInTheDocument()
  })

  it('lands authenticated users on the dashboard', async () => {
    renderApp('/')
    expect(await screen.findByRole('link', { name: 'Dashboard' })).toHaveAttribute(
      'aria-current',
      'page',
    )
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
  })

  it('opens deliveries, invoices, payments, and upload pages', async () => {
    renderApp('/deliveries')
    expect(await screen.findByRole('heading', { name: 'Deliveries' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Add delivery' })).toBeInTheDocument()

    cleanup()
    renderApp('/invoices')
    expect(await screen.findByRole('heading', { name: 'Invoices' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Create invoice' })).toBeInTheDocument()

    cleanup()
    renderApp('/payments')
    expect(await screen.findByRole('heading', { name: 'Payments' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Record payment' })).toBeInTheDocument()

    cleanup()
    renderApp('/upload')
    expect(await screen.findByRole('heading', { name: 'Upload Documents' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Upload' })).toHaveAttribute('aria-current', 'page')
  })

  it('sends anonymous users to login', async () => {
    authState.user = null
    authState.token = null
    renderApp('/hostels')
    expect(await screen.findByRole('button', { name: 'Sign in' })).toBeInTheDocument()
  })

  it('logs out and returns to login', async () => {
    const user = userEvent.setup()
    renderApp('/hostels')
    await user.click(await screen.findByRole('button', { name: 'Log out' }))
    expect(authState.logout).toHaveBeenCalled()
    expect(await screen.findByRole('button', { name: 'Sign in' })).toBeInTheDocument()
  })
})
