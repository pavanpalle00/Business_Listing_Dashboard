import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import ChartTooltip from './ChartTooltip'

// Fixed categorical order - a source keeps its colour whatever the filters do.
const SERIES = ['var(--series-1)', 'var(--series-2)', 'var(--series-3)', 'var(--series-4)']
const fmt = new Intl.NumberFormat('en-IN')

export default function SourcePieChart({ items, total, allSources, selected, onSelect }) {
  // colour follows the source name (its index in the full list), never its rank
  const colorOf = (label) => SERIES[Math.max(0, allSources.indexOf(label)) % SERIES.length]

  return (
    <div className="pie-layout">
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={items}
            dataKey="count"
            nameKey="label"
            innerRadius="58%"
            outerRadius="88%"
            paddingAngle={1}
            stroke="var(--surface)"
            strokeWidth={2}
            cursor="pointer"
            onClick={(entry) => onSelect(entry.label ?? entry.payload?.label)}
            isAnimationActive={false}
          >
            {items.map((item) => (
              <Cell key={item.label} fill={colorOf(item.label)}
                opacity={selected && selected !== item.label ? 0.35 : 1} />
            ))}
          </Pie>
          <Tooltip content={<ChartTooltip total={total} />} />
          <text x="50%" y="47%" textAnchor="middle" className="donut-value">{fmt.format(total)}</text>
          <text x="50%" y="57%" textAnchor="middle" className="donut-caption">listings</text>
        </PieChart>
      </ResponsiveContainer>

      <ul className="legend">
        {items.map((item) => (
          <li key={item.label}>
            <button type="button" onClick={() => onSelect(item.label)} aria-pressed={selected === item.label}>
              <span className="swatch" style={{ background: colorOf(item.label) }} />
              <span className="legend-label">{item.label}</span>
              <span className="legend-value">
                {fmt.format(item.count)} <small>({((item.count / total) * 100).toFixed(0)}%)</small>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
