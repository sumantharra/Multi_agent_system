import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { DOCUMENT_POLL_MS } from '../types/document'
import { UploadDocumentsPage } from './UploadDocumentsPage'

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

const queuedDocument = {
  id: 'doc-1',
  hostel_id: 'h1',
  file_name: 'invoice.pdf',
  storage_key: 'h1/doc-1.pdf',
  mime_type: 'application/pdf',
  document_type: 'invoice',
  processing_status: 'queued',
  extraction_status: 'not_started',
  extracted_payload: null,
  extraction_issues: null,
  content_hash: 'abc',
  uploaded_by: null,
  confirmed_at: null,
  confirmed_by: null,
  rejected_at: null,
  rejected_by: null,
  rejection_reason: null,
  created_at: '2026-09-09T00:00:00Z',
}

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function chooseFile(file: File) {
  const input = screen.getByLabelText('PDF file') as HTMLInputElement
  fireEvent.change(input, { target: { files: [file] } })
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <UploadDocumentsPage />
    </QueryClientProvider>,
  )
}

describe('UploadDocumentsPage', () => {
  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('uploads a PDF and shows it in the recent list', async () => {
    const user = userEvent.setup()
    let uploaded = false
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.includes('/api/v1/hostels')) {
          return jsonResponse({ items: [hostel], page: 1, page_size: 100, total: 1 })
        }
        if (url.includes('/api/v1/documents/upload') && init?.method === 'POST') {
          expect(init.body).toBeInstanceOf(FormData)
          uploaded = true
          return jsonResponse(queuedDocument, 201)
        }
        if (url.includes('/api/v1/documents/doc-1')) {
          return jsonResponse(queuedDocument)
        }
        if (url.includes('/api/v1/documents')) {
          return jsonResponse({
            items: uploaded ? [queuedDocument] : [],
            page: 1,
            page_size: 20,
            total: uploaded ? 1 : 0,
          })
        }
        return jsonResponse({}, 404)
      }),
    )

    renderPage()
    expect(await screen.findByText('No documents yet. Upload a PDF above.')).toBeInTheDocument()
    await screen.findAllByRole('option', { name: 'Sai Hostel (sai-01)' })
    await user.selectOptions(screen.getByLabelText('Hostel'), 'h1')
    chooseFile(new File(['%PDF-1.4'], 'invoice.pdf', { type: 'application/pdf' }))
    await user.click(screen.getByRole('button', { name: 'Upload PDF' }))
    expect(await screen.findByText('invoice.pdf')).toBeInTheDocument()
    expect(screen.getByText('Queued')).toBeInTheDocument()
  })

  it('shows a clear error for a non-PDF file and does not upload', async () => {
    const user = userEvent.setup()
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/api/v1/hostels')) {
        return jsonResponse({ items: [hostel], page: 1, page_size: 100, total: 1 })
      }
      if (url.includes('/api/v1/documents')) {
        return jsonResponse({ items: [], page: 1, page_size: 20, total: 0 })
      }
      return jsonResponse({}, 404)
    })
    vi.stubGlobal('fetch', fetchMock)

    renderPage()
    await screen.findAllByRole('option', { name: 'Sai Hostel (sai-01)' })
    await user.selectOptions(screen.getByLabelText('Hostel'), 'h1')
    chooseFile(new File(['hello'], 'notes.txt', { type: 'text/plain' }))
    expect(await screen.findByText('Only PDF files are allowed')).toBeInTheDocument()
    expect(
      fetchMock.mock.calls.some((call) => {
        const url = String(call[0])
        const init = call[1]
        return url.includes('/upload') && init?.method === 'POST'
      }),
    ).toBe(false)
  })

  it('stops polling once status is pending_review and shows a banner', async () => {
    const user = userEvent.setup()
    let documentGets = 0
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.includes('/api/v1/hostels')) {
          return jsonResponse({ items: [hostel], page: 1, page_size: 100, total: 1 })
        }
        if (url.includes('/api/v1/documents/upload') && init?.method === 'POST') {
          return jsonResponse(queuedDocument, 201)
        }
        if (url.includes('/api/v1/documents/doc-1')) {
          documentGets += 1
          if (documentGets >= 2) {
            return jsonResponse({ ...queuedDocument, processing_status: 'pending_review' })
          }
          return jsonResponse(queuedDocument)
        }
        if (url.includes('/api/v1/documents')) {
          return jsonResponse({ items: [queuedDocument], page: 1, page_size: 20, total: 1 })
        }
        return jsonResponse({}, 404)
      }),
    )

    renderPage()
    await screen.findAllByRole('option', { name: 'Sai Hostel (sai-01)' })
    await user.selectOptions(screen.getByLabelText('Hostel'), 'h1')
    chooseFile(new File(['%PDF-1.4'], 'invoice.pdf', { type: 'application/pdf' }))
    await user.click(screen.getByRole('button', { name: 'Upload PDF' }))
    expect(await screen.findByText('invoice.pdf')).toBeInTheDocument()

    await waitFor(
      () => {
        expect(screen.getByText('Processing finished. Status: Pending review.')).toBeInTheDocument()
        expect(screen.getByText('Pending review')).toBeInTheDocument()
      },
      { timeout: DOCUMENT_POLL_MS + 2000 },
    )

    const getsAfterBanner = documentGets
    await new Promise((resolve) => setTimeout(resolve, DOCUMENT_POLL_MS + 500))
    expect(documentGets).toBe(getsAfterBanner)
  }, 12_000)
})
