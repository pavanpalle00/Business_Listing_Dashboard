const fmt = new Intl.NumberFormat('en-IN')

export default function StatCards({ summary }) {
  const phonePct = summary.total_listings
    ? Math.round((summary.with_phone / summary.total_listings) * 100)
    : 0

  const cards = [
    { label: 'Total listings', value: fmt.format(summary.total_listings) },
    { label: 'Cities', value: summary.cities },
    { label: 'Categories', value: summary.categories },
    { label: 'Sources', value: summary.sources },
    { label: 'With phone number', value: `${phonePct}%`, hint: `${fmt.format(summary.with_phone)} listings` },
  ]

  return (
    <section className="stat-grid" aria-label="Summary">
      {cards.map((card) => (
        <div key={card.label} className="stat-card">
          <span className="stat-label">{card.label}</span>
          <span className="stat-value">{card.value}</span>
          {card.hint && <span className="stat-hint">{card.hint}</span>}
        </div>
      ))}
    </section>
  )
}
