const fmt = new Intl.NumberFormat('en-IN')

/** Shared hover tooltip: label, count and share of the total. */
export default function ChartTooltip({ active, payload, total }) {
  if (!active || !payload?.length) return null
  const { label, count } = payload[0].payload
  const share = total ? ((count / total) * 100).toFixed(1) : '0'

  return (
    <div className="chart-tooltip">
      <strong>{label}</strong>
      <span>{fmt.format(count)} listings · {share}%</span>
    </div>
  )
}
