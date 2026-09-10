export type ProcessingStatus =
  | 'queued'
  | 'processing'
  | 'extracted'
  | 'pending_review'
  | 'confirmed'
  | 'rejected'
  | 'failed'

export type DocumentType = 'invoice' | 'contract' | 'agreement' | 'statement' | 'other'

export type DocumentRecord = {
  id: string
  hostel_id: string
  file_name: string
  storage_key: string
  mime_type: string
  document_type: DocumentType
  processing_status: ProcessingStatus
  extraction_status: string
  extracted_payload: Record<string, unknown> | null
  extraction_issues: Record<string, unknown>[] | null
  content_hash: string | null
  uploaded_by: string | null
  confirmed_at: string | null
  confirmed_by: string | null
  rejected_at: string | null
  rejected_by: string | null
  rejection_reason: string | null
  created_at: string
}

export type PaginatedDocuments = {
  items: DocumentRecord[]
  page: number
  page_size: number
  total: number
}

export const DOCUMENT_TYPES: DocumentType[] = [
  'invoice',
  'contract',
  'agreement',
  'statement',
  'other',
]

export const ACTIVE_PROCESSING_STATUSES: ProcessingStatus[] = ['queued', 'processing']

export const TERMINAL_PROCESSING_STATUSES: ProcessingStatus[] = [
  'pending_review',
  'confirmed',
  'rejected',
  'failed',
]

export const DOCUMENT_POLL_MS = 3000
