import { apiGet, apiPostForm } from './client'
import { withQuery } from './errors'
import type { DocumentRecord, PaginatedDocuments } from '../types/document'

export function listDocuments(
  filters: { hostel_id?: string; processing_status?: string; page?: number; page_size?: number } = {},
  signal?: AbortSignal,
): Promise<PaginatedDocuments> {
  return apiGet(
    withQuery('/api/v1/documents', {
      page: String(filters.page ?? 1),
      page_size: String(filters.page_size ?? 20),
      hostel_id: filters.hostel_id,
      processing_status: filters.processing_status,
    }),
    signal,
  )
}

export function getDocument(id: string, signal?: AbortSignal): Promise<DocumentRecord> {
  return apiGet<DocumentRecord>(`/api/v1/documents/${id}`, signal)
}

export function uploadDocument(payload: {
  hostel_id: string
  document_type: string
  file: File
}): Promise<DocumentRecord> {
  const form = new FormData()
  form.append('hostel_id', payload.hostel_id)
  form.append('document_type', payload.document_type)
  form.append('file', payload.file)
  return apiPostForm<DocumentRecord>('/api/v1/documents/upload', form)
}
