import { useEffect, useState } from 'react'
import { api } from '../api/client'

/**
 * Loads everything the dashboard needs for the current filters.
 *
 * Each chart is filtered by the *other* dimensions only, so the city chart
 * keeps showing every city (with the selected one highlighted) while the
 * category and source charts narrow down to that city.
 */
export function useDashboardData(filters) {
  const { city, category, source } = filters
  const key = `${city}|${category}|${source}`
  // `key` records which filter selection the stored response belongs to
  const [state, setState] = useState({ key: null, data: null, error: null })

  useEffect(() => {
    let cancelled = false // ignore responses from an outdated filter selection

    Promise.all([
      api.summary({ city, category, source }),
      api.cityCount({ category, source }),
      api.categoryCount({ city, source }),
      api.sourceCount({ city, category }),
    ])
      .then(([summary, cities, categories, sources]) => {
        if (!cancelled) setState({ key, data: { summary, cities, categories, sources }, error: null })
      })
      .catch((error) => {
        if (!cancelled) setState((prev) => ({ key, data: prev.data, error: error.message }))
      })

    return () => {
      cancelled = true
    }
  }, [key, city, category, source])

  // keep showing the previous data while the new selection loads
  return { data: state.data, error: state.error, loading: state.key !== key }
}

/** Unfiltered labels for the filter dropdowns (loaded once). */
export function useFilterOptions() {
  const [options, setOptions] = useState({ cities: [], categories: [], sources: [] })

  useEffect(() => {
    Promise.all([api.cityCount(), api.categoryCount(), api.sourceCount()])
      .then(([cities, categories, sources]) =>
        setOptions({
          cities: cities.items.map((i) => i.label).sort(),
          categories: categories.items.map((i) => i.label).sort(),
          sources: sources.items.map((i) => i.label).sort(),
        }),
      )
      .catch(() => {}) // the main data hook already reports connection errors
  }, [])

  return options
}
