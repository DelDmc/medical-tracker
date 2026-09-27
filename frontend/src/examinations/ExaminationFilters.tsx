import { useQuery } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import type { SetURLSearchParams } from 'react-router'

import { CATEGORIES_QUERY_KEY, listCategories } from '../api/examinations'
import { EXAMINATION_STATUSES } from '../api/types'
import styles from './ExaminationFilters.module.css'
import { STATUS_LABELS } from './presentation'

export const FILTER_KEYS = ['search', 'status', 'category', 'ordering'] as const

type ExaminationFiltersProps = {
  searchParams: URLSearchParams
  setSearchParams: SetURLSearchParams
}

/**
 * Title search, status and category filters, and scheduled-date ordering
 * (ADS-FR-028-01 … ADS-FR-030-01). The URL holds the chosen values, so the backend
 * applies them and the browser's history keeps them.
 */
export function ExaminationFilters({ searchParams, setSearchParams }: ExaminationFiltersProps) {
  const [search, setSearch] = useState(searchParams.get('search') ?? '')
  const categories = useQuery({
    queryKey: CATEGORIES_QUERY_KEY,
    queryFn: listCategories,
    staleTime: Infinity,
  })

  function setParam(key: string, value: string) {
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      if (value) next.set(key, value)
      else next.delete(key)
      return next
    })
  }

  function onSearch(event: FormEvent) {
    event.preventDefault()
    setParam('search', search.trim())
  }

  function clearFilters() {
    setSearch('')
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      for (const key of FILTER_KEYS) next.delete(key)
      return next
    })
  }

  const active = FILTER_KEYS.some((key) => searchParams.get(key))

  return (
    <form
      className={`card ${styles.filters}`}
      role="search"
      aria-label="Search and filter examinations"
      onSubmit={onSearch}
    >
      <div className={styles.searchRow}>
        <div className="field">
          <label className="field-label" htmlFor="filter-search">
            Search titles
          </label>
          <input
            id="filter-search"
            className="input"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <button className="button button-primary" type="submit">
          Search
        </button>
      </div>
      <div className={styles.selects}>
        <div className="field">
          <label className="field-label" htmlFor="filter-status">
            Status
          </label>
          <select
            id="filter-status"
            className="input"
            value={searchParams.get('status') ?? ''}
            onChange={(event) => setParam('status', event.target.value)}
          >
            <option value="">All statuses</option>
            {EXAMINATION_STATUSES.map((status) => (
              <option key={status} value={status}>
                {STATUS_LABELS[status]}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="field-label" htmlFor="filter-category">
            Category
          </label>
          <select
            id="filter-category"
            className="input"
            value={searchParams.get('category') ?? ''}
            onChange={(event) => setParam('category', event.target.value)}
          >
            <option value="">All categories</option>
            {(categories.data ?? []).map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="field-label" htmlFor="filter-ordering">
            Order
          </label>
          <select
            id="filter-ordering"
            className="input"
            value={searchParams.get('ordering') ?? ''}
            onChange={(event) => setParam('ordering', event.target.value)}
          >
            <option value="">Date added, oldest first</option>
            <option value="scheduled_date">Scheduled date, earliest first</option>
            <option value="-scheduled_date">Scheduled date, latest first</option>
          </select>
        </div>
      </div>
      {active ? (
        <div className="button-row">
          <button className="button button-secondary" type="button" onClick={clearFilters}>
            Clear filters
          </button>
        </div>
      ) : null}
    </form>
  )
}
