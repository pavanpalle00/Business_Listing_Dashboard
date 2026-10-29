const FIELDS = [
  { key: 'city', label: 'City', optionsKey: 'cities', allLabel: 'All cities' },
  { key: 'category', label: 'Category', optionsKey: 'categories', allLabel: 'All categories' },
  { key: 'source', label: 'Source', optionsKey: 'sources', allLabel: 'All sources' },
]

export default function FilterBar({ filters, options, onChange, onReset }) {
  const active = Object.values(filters).some(Boolean)

  return (
    <div className="filter-bar" role="search">
      {FIELDS.map(({ key, label, optionsKey, allLabel }) => (
        <label key={key} className="filter">
          <span>{label}</span>
          <select value={filters[key]} onChange={(e) => onChange(key, e.target.value)}>
            <option value="">{allLabel}</option>
            {options[optionsKey].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
        </label>
      ))}
      <button type="button" className="btn-ghost" onClick={onReset} disabled={!active}>
        Clear filters
      </button>
    </div>
  )
}
