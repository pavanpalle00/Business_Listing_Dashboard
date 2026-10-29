import { useEffect, useState } from 'react'
import { api } from '../api/client'

const PAGE_SIZE = 10

/** Paginated, searchable table of the raw rows behind the charts. */
export default function ListingsTable({ filters }) {
  const [search, setSearch] = useState('')
  const [debounced, setDebounced] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // wait until the user stops typing before calling the API
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(search.trim()), 300)
    return () => clearTimeout(timer)
  }, [search])

  // the page number belongs to one query; new filters or search -> back to page 1
  const queryKey = JSON.stringify([filters, debounced])
  const [paging, setPaging] = useState({ queryKey, page: 1 })
  const page = paging.queryKey === queryKey ? paging.page : 1
  const setPage = (next) => setPaging({ queryKey, page: next })

  useEffect(() => {
    let cancelled = false
    api.listings({ ...filters, search: debounced, page, page_size: PAGE_SIZE })
      .then((data) => !cancelled && (setResult(data), setError(null)))
      .catch((err) => !cancelled && setError(err.message))
    return () => {
      cancelled = true
    }
  }, [filters, debounced, page])

  return (
    <section className="card card-wide">
      <header className="card-header">
        <div>
          <h2>Listings</h2>
          <p className="card-subtitle">{result ? `${result.total} matching listings` : 'Loading…'}</p>
        </div>
        <input
          type="search"
          className="search"
          placeholder="Search business name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search business name"
        />
      </header>

      {error && <p className="error-inline">{error}</p>}

      <div className="table-scroll">
        <table className="data-table listings">
          <thead>
            <tr>
              <th>Business</th><th>Category</th><th>City</th><th>Address</th><th>Phone</th><th>Source</th>
            </tr>
          </thead>
          <tbody>
            {result?.items.map((row) => (
              <tr key={row.id}>
                <td className="strong">{row.business_name}</td>
                <td>{row.category}</td>
                <td>{row.city}</td>
                <td className="address">{row.address ?? <span className="muted">—</span>}</td>
                <td className="nowrap">{row.phone ?? <span className="muted">—</span>}</td>
                <td><span className="pill">{row.source}</span></td>
              </tr>
            ))}
            {result && result.items.length === 0 && (
              <tr><td colSpan={6} className="empty">No listings found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {result && result.pages > 1 && (
        <nav className="pager" aria-label="Pagination">
          <button type="button" className="btn-ghost" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            ← Previous
          </button>
          <span>Page {page} of {result.pages}</span>
          <button type="button" className="btn-ghost" disabled={page >= result.pages} onClick={() => setPage(page + 1)}>
            Next →
          </button>
        </nav>
      )}
    </section>
  )
}
