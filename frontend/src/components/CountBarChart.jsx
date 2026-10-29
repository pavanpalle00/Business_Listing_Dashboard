import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import ChartTooltip from './ChartTooltip'

/**
 * One-series bar chart for {label, count} items.
 * - vertical bars (default) for a handful of short labels (cities)
 * - horizontal bars for many / longer labels (categories)
 * Clicking a bar toggles it as a filter; the selected bar stays strong while
 * the others are muted.
 */
export default function CountBarChart({ items, total, horizontal = false, selected, onSelect }) {
  const barColor = (label) => (selected && selected !== label ? 'var(--series-1-muted)' : 'var(--series-1)')
  const height = horizontal ? Math.max(260, items.length * 34) : 300
  const radius = horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0] // round only the data end

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={items}
        layout={horizontal ? 'vertical' : 'horizontal'}
        margin={{ top: 20, right: horizontal ? 48 : 8, bottom: 0, left: 0 }}
        barCategoryGap={horizontal ? 6 : '22%'}
      >
        <CartesianGrid
          stroke="var(--grid)"
          vertical={horizontal}
          horizontal={!horizontal}
        />
        {horizontal ? (
          <>
            <XAxis type="number" allowDecimals={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="label" width={110} tick={{ fill: 'var(--text-secondary)', fontSize: 13 }}
              axisLine={{ stroke: 'var(--axis)' }} tickLine={false} />
          </>
        ) : (
          <>
            <XAxis dataKey="label" interval={0} tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              axisLine={{ stroke: 'var(--axis)' }} tickLine={false} />
            <YAxis allowDecimals={false} width={40} tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              axisLine={false} tickLine={false} />
          </>
        )}
        <Tooltip cursor={{ fill: 'var(--hover-wash)' }} content={<ChartTooltip total={total} />} />
        <Bar dataKey="count" radius={radius} cursor="pointer" maxBarSize={horizontal ? 22 : 56} isAnimationActive={false}
          onClick={(entry) => onSelect(entry.label ?? entry.payload?.label)}>
          {items.map((item) => (
            <Cell key={item.label} fill={barColor(item.label)} />
          ))}
          <LabelList dataKey="count" position={horizontal ? 'right' : 'top'}
            style={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
