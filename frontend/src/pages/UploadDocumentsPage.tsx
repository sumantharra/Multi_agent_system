import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getDocument, listDocuments, uploadDocument } from '../api/documents'
import { apiErrorMessage } from '../api/errors'
import { listHostels } from '../api/hostels'
import { PageEmpty, PageError, PageLoading } from '../components/PageState'
import {
  ACTIVE_PROCESSING_STATUSES,
  DOCUMENT_POLL_MS,
  DOCUMENT_TYPES,
  TERMINAL_PROCESSING_STATUSES,
  type DocumentRecord,
  type DocumentType,
  type PaginatedDocuments,
  type ProcessingStatus,
} from '../types/document'
import { hostelLabel } from '../utils/hostels'

const fieldClass = 'rounded-xl border border-slate-200 px-3 py-2'

const typeLabels: Record<DocumentType, string> = {
  invoice: 'Invoice',
  contract: 'Contract',
  agreement: 'Agreement',
  statement: 'Statement',
  other: 'Other',
}

const statusLabels: Record<ProcessingStatus, string> = {
  queued: 'Queued',
  processing: 'Processing',
  extracted: 'Extracted',
  pending_review: 'Pending review',
  confirmed: 'Confirmed',
  rejected: 'Rejected',
  failed: 'Failed',
}

function isPdfFile(file: File): boolean {
  return file.name.toLowerCase().endsWith('.pdf')
}

function statusBadgeClass(status: ProcessingStatus): string {
  if (status === 'confirmed') {
    return 'bg-emerald-100 text-emerald-800'
  }
  if (status === 'failed' || status === 'rejected') {
    return 'bg-red-100 text-red-800'
  }
  if (status === 'pending_review' || status === 'extracted') {
    return 'bg-sky-100 text-sky-800'
  }
  if (status === 'processing') {
    return 'bg-amber-100 text-amber-800'
  }
  return 'bg-slate-100 text-slate-700'
}

function mergeDocument(items: DocumentRecord[], next: DocumentRecord): DocumentRecord[] {
  const exists = items.some((item) => item.id === next.id)
  if (!exists) {
    return [next, ...items]
  }
  return items.map((item) => (item.id === next.id ? next : item))
}

export function UploadDocumentsPage() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [hostelId, setHostelId] = useState('')
  const [documentType, setDocumentType] = useState<DocumentType>('invoice')
  const [file, setFile] = useState<File | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [watchedId, setWatchedId] = useState<string | null>(null)
  const [banner, setBanner] = useState<string | null>(null)

  const hostelsQuery = useQuery({
    queryKey: ['hostels'],
    queryFn: ({ signal }) => listHostels(signal),
  })

  const documentsQuery = useQuery({
    queryKey: ['documents'],
    queryFn: ({ signal }) => listDocuments({ page: 1, page_size: 20 }, signal),
  })

  const watchedQuery = useQuery({
    queryKey: ['document', watchedId],
    queryFn: ({ signal }) => getDocument(watchedId!, signal),
    enabled: Boolean(watchedId),
    refetchInterval: (query) => {
      const status = query.state.data?.processing_status
      if (status && ACTIVE_PROCESSING_STATUSES.includes(status)) {
        return DOCUMENT_POLL_MS
      }
      return false
    },
  })

  useEffect(() => {
    const document = watchedQuery.data
    if (!document) {
      return
    }
    queryClient.setQueryData(['documents'], (current: PaginatedDocuments | undefined) => {
      if (!current) {
        return current
      }
      return { ...current, items: mergeDocument(current.items, document) }
    })
    if (TERMINAL_PROCESSING_STATUSES.includes(document.processing_status)) {
      setBanner(`Processing finished. Status: ${statusLabels[document.processing_status]}.`)
    }
  }, [queryClient, watchedQuery.data])

  const uploadMutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: async (document) => {
      setFormError(null)
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      setWatchedId(document.id)
      if (TERMINAL_PROCESSING_STATUSES.includes(document.processing_status)) {
        setBanner(`Processing finished. Status: ${statusLabels[document.processing_status]}.`)
      } else {
        setBanner(null)
      }
      queryClient.setQueryData(['documents'], (current: PaginatedDocuments | undefined) => {
        if (!current) {
          return { items: [document], page: 1, page_size: 20, total: 1 }
        }
        return {
          ...current,
          items: mergeDocument(current.items, document),
          total: current.items.some((item) => item.id === document.id)
            ? current.total
            : current.total + 1,
        }
      })
      await queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    onError: (error: unknown) => {
      setFormError(apiErrorMessage(error, 'Could not upload document'))
    },
  })

  const hostels = hostelsQuery.data?.items ?? []
  const items = documentsQuery.data?.items ?? []

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    if (!file) {
      setFormError('Choose a PDF file')
      return
    }
    if (!isPdfFile(file)) {
      setFormError('Only PDF files are allowed')
      return
    }
    uploadMutation.mutate({
      hostel_id: hostelId,
      document_type: documentType,
      file,
    })
  }

  return (
    <div className="mx-auto w-full max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Upload Documents</h1>
      <p className="mt-2 text-slate-600">
        Store original PDFs. Processing status updates on this page; you can leave and come back.
      </p>

      {banner && (
        <p className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900" role="status">
          {banner}
        </p>
      )}

      <section className="mt-8 mb-8 rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Upload PDF</h2>
        <form className="mt-6 grid gap-4 sm:grid-cols-2" onSubmit={onSubmit}>
          <label className="grid gap-1 text-sm text-slate-700">
            Hostel
            <select
              required
              className={fieldClass}
              value={hostelId}
              onChange={(event) => setHostelId(event.target.value)}
            >
              <option value="">Select hostel</option>
              {hostels
                .filter((hostel) => hostel.active)
                .map((hostel) => (
                  <option key={hostel.id} value={hostel.id}>
                    {hostel.name} ({hostel.code})
                  </option>
                ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm text-slate-700">
            Document type
            <select
              required
              className={fieldClass}
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value as DocumentType)}
            >
              {DOCUMENT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {typeLabels[type]}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm text-slate-700 sm:col-span-2">
            PDF file
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              className={fieldClass}
              onChange={(event) => {
                const next = event.target.files?.[0] ?? null
                setFile(next)
                if (next && !isPdfFile(next)) {
                  setFormError('Only PDF files are allowed')
                } else {
                  setFormError(null)
                }
              }}
            />
          </label>
          {formError && (
            <p className="sm:col-span-2 text-sm text-red-600" role="alert">
              {formError}
            </p>
          )}
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={uploadMutation.isPending}
              className="rounded-xl bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
            >
              {uploadMutation.isPending ? 'Uploading…' : 'Upload PDF'}
            </button>
          </div>
        </form>
      </section>

      <section className="rounded-3xl border border-emerald-100 bg-white p-6 shadow-xl shadow-emerald-950/5 sm:p-8">
        <h2 className="text-lg font-semibold text-slate-900">Recent uploads</h2>
        {documentsQuery.isLoading && <PageLoading message="Loading documents…" />}
        {documentsQuery.isError && (
          <PageError message="Could not load documents. Is the backend running?" />
        )}
        {documentsQuery.isSuccess && items.length === 0 && (
          <PageEmpty message="No documents yet. Upload a PDF above." />
        )}
        {items.length > 0 && (
          <ul className="mt-6 divide-y divide-slate-100">
            {items.map((document) => (
              <li key={document.id} className="flex flex-wrap items-center justify-between gap-3 py-4">
                <div>
                  <p className="font-semibold text-slate-900">{document.file_name}</p>
                  <p className="text-sm text-slate-600">
                    {hostelLabel(hostels, document.hostel_id)} ·{' '}
                    {typeLabels[document.document_type] ?? document.document_type}
                  </p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadgeClass(document.processing_status)}`}
                >
                  {statusLabels[document.processing_status]}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
