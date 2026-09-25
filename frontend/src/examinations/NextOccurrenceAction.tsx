import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router'

import { createNextOccurrence, examinationKeys } from '../api/examinations'
import type { Examination } from '../api/types'
import { errorsFromFailure, NON_FIELD } from '../forms/errors'
import { FormAlert } from '../forms/FormField'

/**
 * Create the next occurrence of a recurring examination (user_flows.md §19). A repeat
 * of the request returns the occurrence already created, which is treated exactly
 * like a fresh creation.
 */
export function NextOccurrenceAction({ examination }: { examination: Examination }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: () => createNextOccurrence(examination.id),
    onSuccess: async (occurrence) => {
      queryClient.setQueryData(examinationKeys.detail(occurrence.id), occurrence)
      await queryClient.invalidateQueries({ queryKey: examinationKeys.all })
      navigate(`/examinations/${occurrence.id}`, {
        state: { message: 'This is the next occurrence. Its reminder and recurrence start empty.' },
      })
    },
  })
  const failure = mutation.isError ? errorsFromFailure(mutation.error)[NON_FIELD] : undefined

  return (
    <div className="stack">
      <FormAlert messages={failure ?? (mutation.isError ? ['Please try again.'] : undefined)} />
      <div className="button-row">
        <button
          className="button button-secondary"
          type="button"
          disabled={mutation.isPending}
          onClick={() => mutation.mutate()}
        >
          {mutation.isPending ? 'Creating…' : 'Create next occurrence'}
        </button>
      </div>
    </div>
  )
}
