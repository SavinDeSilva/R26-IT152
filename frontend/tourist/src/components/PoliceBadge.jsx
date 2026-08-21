/** Police badge — lagoon teal + sand gold */
export default function PoliceBadge({ size = 44 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      style={{ display: 'block' }}
    >
      <path
        d="M32 4L52 12V30C52 44 42 54 32 60C22 54 12 44 12 30V12L32 4Z"
        fill="#0A4A52"
      />
      <path
        d="M32 10L46 16V30C46 40.5 38.5 48.5 32 53.5C25.5 48.5 18 40.5 18 30V16L32 10Z"
        fill="#12707A"
      />
      <circle cx="32" cy="30" r="11" fill="#DDF2F3" />
      <path
        d="M32 21L34.8 27.2L41.5 28L36.5 32.6L37.9 39.2L32 35.8L26.1 39.2L27.5 32.6L22.5 28L29.2 27.2L32 21Z"
        fill="#0A4A52"
      />
      <rect x="26" y="44" width="12" height="3" rx="1" fill="#D4A84B" />
    </svg>
  )
}
