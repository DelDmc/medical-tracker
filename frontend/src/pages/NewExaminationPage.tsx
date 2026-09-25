import { useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router'

import { createExamination, examinationKeys } from '../api/examinations'
import type { ExaminationInput } from '../api/types'
import { ExaminationForm } from '../examinations/ExaminationForm'

export function NewExaminationPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  async function create(input: ExaminationInput) {
    const created = await createExamination(input)
    await queryClient.invalidateQueries({ queryKey: examinationKeys.all })
    const suffix = created.status === 'draft' ? ' as a draft' : ''
    navigate('/examinations', { state: { message: `“${created.title}” was saved${suffix}.` } })
  }

  return (
    <section className="page" aria-labelledby="new-examination-title">
      <h1 id="new-examination-title">Add examination</h1>
      <ExaminationForm
        submitLabel="Save examination"
        allowDraftSave
        onSubmit={create}
        onCancel={() => navigate('/examinations')}
      />
    </section>
  )
}
