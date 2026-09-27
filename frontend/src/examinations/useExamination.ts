import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router'

import { ApiError } from '../api/client'
import { examinationKeys, getExamination } from '../api/examinations'

/** The examination named by the `:id` route parameter. */
export function useExaminationFromRoute() {
  const { id } = useParams()
  const examinationId = Number(id)
  const query = useQuery({
    queryKey: examinationKeys.detail(examinationId),
    queryFn: () => getExamination(examinationId),
    enabled: Number.isInteger(examinationId) && examinationId > 0,
  })
  const notFound =
    !(Number.isInteger(examinationId) && examinationId > 0) ||
    (query.error instanceof ApiError && query.error.status === 404)
  return { examinationId, query, notFound }
}
