import { useEffect, useState } from 'react';

const SLIDES = ['/bgi.jpg', '/itinerary.webp', '/wellness.jpeg', '/sos.jpeg'];
const ROTATE_MS = 8000;

export default function PageBackground() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActive((i) => (i + 1) % SLIDES.length);
    }, ROTATE_MS);
    return () => clearInterval(timer);
  }, []);

  return (
    <>
      <div id="pageBgLayer" aria-hidden="true">
        {SLIDES.map((src, index) => (
          <div
            key={src}
            className={`page-bg-slide${index === active ? ' active' : ''}`}
            style={{ backgroundImage: `url(${src})` }}
          />
        ))}
      </div>
      <div id="pageBgTint" aria-hidden="true" />
    </>
  );
}
