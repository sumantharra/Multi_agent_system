import { useState, type FormEvent } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Navigate, useNavigate } from 'react-router-dom'

import { getBrand } from '../api/auth'
import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export function LoginPage() {
  const { login, user, loading } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@local.test')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const brandQuery = useQuery({
    queryKey: ['brand'],
    queryFn: getBrand,
  })

  if (!loading && user) {
    return <Navigate to="/hostels" replace />
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(email.trim(), password)
      navigate('/hostels', { replace: true })
    } catch (err) {
      if (err instanceof ApiError) {
        const body = err.body as { error?: { message?: string } } | null
        setError(body?.error?.message ?? 'Login failed')
      } else {
        setError('Login failed. Check backend is running.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  const brandName = brandQuery.data?.name ?? 'RR Vijaya Milk Agencies'
  const brandDomain = brandQuery.data?.domain ?? 'rrvijayamilkagencies.com'

  return (
    <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_#e8f5ef,_#f4f8f6_45%,_#eef2f0)] px-6 py-12">
      <section className="w-full max-w-md rounded-3xl border border-emerald-100 bg-white p-8 shadow-xl shadow-emerald-950/5 sm:p-10">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-emerald-700">
          {brandDomain}
        </p>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">{brandName}</h1>
        <p className="mt-2 text-slate-600">Sign in with your email and password to continue.</p>

        <form className="mt-8 grid gap-4" onSubmit={onSubmit}>
          <label className="grid gap-1 text-sm text-slate-700">
            Email
            <input
              required
              type="email"
              autoComplete="username"
              className="rounded-xl border border-slate-200 px-3 py-2"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Password
            <input
              required
              type="password"
              autoComplete="current-password"
              className="rounded-xl border border-slate-200 px-3 py-2"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="mt-2 rounded-xl bg-emerald-700 px-4 py-2.5 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
          >
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </section>
    </main>
  )
}
