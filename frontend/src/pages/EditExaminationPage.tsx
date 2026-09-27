import { useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router'

import { examinationKeys, updateExamination } from '../api/examinations'
import type { ExaminationInput } from '../api/types'
import { ExaminationForm } from '../examinations/ExaminationForm'
import { ExaminationLoadError, ExaminationNotFound } from '../examinations/ExaminationStatusView'
import { useExaminationFromRoute } from '../examinations/useExamination'

export function EditExaminationPage() {
  const { examinationId, query, notFound } = useExaminationFromRoute()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  async function save(input: ExaminationInput) {
    const updated = await updateExamination(examinationId, input)
    queryClient.setQueryData(examinationKeys.detail(examinationId), updated)
    await queryClient.invalidateQueries({ queryKey: examinationKeys.all })
    navigate(`/examinations/${examinationId}`, { state: { message: 'Your changes were saved.' } })
  }

  if (notFound) return <ExaminationNotFound />
  if (query.isPending) {
    return (
      <p className="muted" role="status">
        Loading examination…
      </p>
    )
  }
  if (query.isError) return <ExaminationLoadError onRetry={() => query.refetch()} />

  return (
    <section className="page" aria-labelledby="edit-examination-title">
      <h1 id="edit-examination-title">Edit examination</h1>
      <ExaminationForm
        examination={query.data}
        submitLabel="Save changes"
        onSubmit={save}
        onCancel={() => navigate(`/examinations/${examinationId}`)}
      />
    </section>
  )
}
