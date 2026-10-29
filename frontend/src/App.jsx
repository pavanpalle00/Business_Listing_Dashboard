import { useCallback, useState } from 'react'
import ChartCard from './components/ChartCard'
import CountBarChart from './components/CountBarChart'
import FilterBar from './components/FilterBar'
import ListingsTable from './components/ListingsTable'
import SourcePieChart from './components/SourcePieChart'
import StatCards from './components/StatCards'
import { useDashboardData, useFilterOptions } from './hooks/useDashboardData'
import { useMediaQuery } from './hooks/useMediaQuery'

const EMPTY_FILTERS = { city: '', category: '', source: '' }

export default function App() {
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const { data, loading, error } = useDashboardData(filters)
  const options = useFilterOptions()
  const isNarrow = useMediaQuery('(max-width: 640px)') // city names collide as vertical bars on phones

  const setFilter = useCallback((key, value) => setFilters((f) => ({ ...f, [key]: value })), [])
  // clicking the already-selected bar/slice clears that filter
  const toggleFilter = useCallback(
    (key) => (value) => setFilters((f) => ({ ...f, [key]: f[key] === value ? '' : value })),
    [],
  )

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Business Listings Dashboard</h1>
          <p className="muted">
            Listings scraped from OpenStreetMap and Wikipedia · stored in MySQL · served by FastAPI
          </p>
        </div>
        {loading && data && <span className="loading-dot" aria-live="polite">Updating…</span>}
      </header>

      <FilterBar filters={filters} options={options} onChange={setFilter} onReset={() => setFilters(EMPTY_FILTERS)} />

      {error && (
        <div className="error-banner" role="alert">
          <strong>Could not load dashboard data.</strong> {error}. Is the FastAPI server running on port 8000?
        </div>
      )}

      {!data && loading && <div className="skeleton" aria-busy="true">Loading dashboard…</div>}

      {data && (
        <>
          <StatCards summary={data.summary} />

          <div className="grid">
            <ChartCard title="Businesses by city" data={data.cities} labelHeader="City" className="card-wide">
              <CountBarChart horizontal={isNarrow} items={data.cities.items} total={data.cities.total}
                selected={filters.city} onSelect={toggleFilter('city')} />
            </ChartCard>

            <ChartCard title="Businesses by category" data={data.categories} labelHeader="Category">
              <CountBarChart horizontal items={data.categories.items} total={data.categories.total}
                selected={filters.category} onSelect={toggleFilter('category')} />
            </ChartCard>

            <ChartCard title="Businesses by source" data={data.sources} labelHeader="Source">
              <SourcePieChart items={data.sources.items} total={data.sources.total}
                allSources={options.sources} selected={filters.source} onSelect={toggleFilter('source')} />
            </ChartCard>

            <ListingsTable filters={filters} />
          </div>
        </>
      )}

      <footer className="page-footer muted">
        Data © OpenStreetMap contributors (ODbL) and Wikipedia (CC BY-SA). Built with React, FastAPI and MySQL.
      </footer>
    </div>
  )
}
