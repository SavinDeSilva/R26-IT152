import { POLICE_LOGO } from '../assets'

/** Sri Lanka Police crest logo */
export default function PoliceBadge({ size = 44 }) {
  return (
    <img
      src={POLICE_LOGO}
      alt="Sri Lanka Police"
      width={size}
      height={size}
      style={{
        display: 'block',
        width: size,
        height: size,
        objectFit: 'contain',
        borderRadius: 4,
        background: '#fff',
        flexShrink: 0,
      }}
    />
  )
}
