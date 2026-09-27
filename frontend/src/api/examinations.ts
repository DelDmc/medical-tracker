import { apiRequest } from './authenticated'
import type { Category, Examination, ExaminationInput } from './types'

export type ExaminationListParams = {
  search?: string
  status?: string
  category?: string
  ordering?: string
  time_state?: string
}

function queryString(params: Record<string, string | undefined>) {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value) search.set(key, value)
  }
  const text = search.toString()
  return text ? `?${text}` : ''
}

export function listCategories() {
  return apiRequest<Category[]>('/categories/')
}

export function listExaminations(params: ExaminationListParams = {}) {
  return apiRequest<Examination[]>(`/examinations/${queryString(params)}`)
}

export function getExamination(id: number) {
  return apiRequest<Examination>(`/examinations/${id}/`)
}

export function createExamination(input: ExaminationInput) {
  return apiRequest<Examination>('/examinations/', { method: 'POST', body: input })
}

export function updateExamination(id: number, input: Partial<ExaminationInput>) {
  return apiRequest<Examination>(`/examinations/${id}/`, { method: 'PATCH', body: input })
}

/**
 * `POST /api/v1/examinations/{id}/next-occurrence/`. A first request creates the
 * occurrence (201) and a repeat returns the same one (200); both mean success.
 */
export function createNextOccurrence(id: number) {
  return apiRequest<Examination>(`/examinations/${id}/next-occurrence/`, { method: 'POST' })
}

export function deleteExamination(id: number) {
  return apiRequest<null>(`/examinations/${id}/`, { method: 'DELETE' })
}

export const examinationKeys = {
  all: ['examinations'] as const,
  list: (params: ExaminationListParams) => ['examinations', 'list', params] as const,
  detail: (id: number) => ['examinations', 'detail', id] as const,
}

export const CATEGORIES_QUERY_KEY = ['categories']
