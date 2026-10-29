import { useState } from 'react'

const fmt = new Intl.NumberFormat('en-IN')

/**
 * Card wrapper for every report: title, total, and a Chart / Table toggle so
 * the numbers are always available as text (accessibility + exact values).
 */
export default function ChartCard({ title, subtitle, data, labelHeader, children, className = '' }) {
  const [view, setView] = useState('chart')

  return (
    <section className={`card ${className}`}>
      <header className="card-header">
        <div>
          <h2>{title}</h2>
          <p className="card-subtitle">{subtitle ?? `${fmt.format(data.total)} listings`}</p>
        </div>
        <div className="toggle" role="group" aria-label={`${title} view`}>
          {['chart', 'table'].map((mode) => (
            <button key={mode} type="button" aria-pressed={view === mode} onClick={() => setView(mode)}>
              {mode === 'chart' ? 'Chart' : 'Table'}
            </button>
          ))}
        </div>
      </header>

      {data.items.length === 0 ? (
        <p className="empty">No listings match the current filters.</p>
      ) : view === 'chart' ? (
        children
      ) : (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr><th>{labelHeader}</th><th className="num">Count</th><th className="num">Share</th></tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.label}>
                  <td>{item.label}</td>
                  <td className="num">{fmt.format(item.count)}</td>
                  <td className="num">{((item.count / data.total) * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
