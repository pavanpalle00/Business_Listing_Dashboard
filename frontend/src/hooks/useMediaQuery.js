import { useEffect, useState } from 'react'

/** true while the CSS media query matches, e.g. useMediaQuery('(max-width: 640px)') */
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches)

  useEffect(() => {
    const media = window.matchMedia(query)
    const onChange = () => setMatches(media.matches)
    media.addEventListener('change', onChange)
    onChange()
    return () => media.removeEventListener('change', onChange)
  }, [query])

  return matches
}
