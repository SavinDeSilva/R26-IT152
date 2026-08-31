import { useState } from 'react';

export default function AttractionPhoto({
  src,
  name,
  gradient = 'linear-gradient(135deg, #1E6E6F, #4EC6D4)',
  height = 160,
  children,
}) {
  const [failed, setFailed] = useState(false);
  const showPhoto = Boolean(src) && !failed;

  return (
    <div
      style={{
        height,
        position: 'relative',
        overflow: 'hidden',
        background: showPhoto ? '#d9ecee' : gradient,
      }}
    >
      {showPhoto && (
        <img
          src={src}
          alt={name || ''}
          loading="lazy"
          decoding="async"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block',
          }}
          onError={() => setFailed(true)}
        />
      )}
      {children}
    </div>
  );
}
