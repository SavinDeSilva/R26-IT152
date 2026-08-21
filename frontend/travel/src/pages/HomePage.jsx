import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { attractionsApi } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { SITES } from '@shared/config';
import AttractionPhoto from '../components/AttractionPhoto';
import { openSosDashboard } from '../api/sosClient';

const MODULES = [
  {
    id: 'itinerary',
    title: 'Itinerary',
    text: 'Pick moods, stays, and a day-by-day Sri Lanka plan.',
    image: '/itinerary.webp',
    to: '/attractions',
  },
  {
    id: 'wellness',
    title: 'Wellness',
    text: 'Match Ayurveda centres and meditation retreats to your profile.',
    image: '/wellness.jpeg',
    href: SITES.wellness,
  },
  {
    id: 'sos',
    title: 'SOS',
    text: 'One-tap emergency help, nearest hospital, and station chat.',
    image: '/sos.jpeg',
    href: SITES.sos,
    sos: true,
  },
  {
    id: 'livedata',
    title: 'Live Data',
    text: 'Crowd risk, green-site alternatives, and live tourism pressure.',
    image: '/images.jpeg',
    href: SITES.livedata,
  },
];

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const [attractions, setAttractions] = useState([]);

  useEffect(() => {
    let cancelled = false;
    attractionsApi
      .list()
      .then(({ data }) => {
        if (cancelled) return;
        const list = data?.attractions || [];
        const withPhotos = list.filter((a) => a.image);
        const picked = (withPhotos.length >= 8 ? withPhotos : list).slice(0, 8);
        setAttractions(picked);
      })
      .catch(() => {
        if (!cancelled) setAttractions([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const itineraryTo = isAuthenticated ? '/attractions' : '/login';

  const openSos = async (e) => {
    e.preventDefault();
    if (isAuthenticated) {
      await openSosDashboard('/');
      return;
    }
    window.location.assign(SITES.sos);
  };

  const featured = useMemo(() => attractions, [attractions]);

  return (
    <div>
      <section className="tc-home-hero">
        <div className="tc-site-wrap tc-home-hero-inner">
          <p className="tc-home-kicker">A team of Sri Lanka travel experts</p>
          <h1>Trust our island experience</h1>
          <p>
            Plan beaches, highlands, wellness retreats, and stay protected — one Tour Ceylon
            dashboard for itinerary, Ayurveda matching, live safety data, and SOS.
          </p>
          <Link className="tc-home-cta" to={itineraryTo}>
            Get in touch
          </Link>
        </div>
      </section>

      <div className="tc-site-wrap">
        <div className="tc-home-modules">
          {MODULES.map((mod) => {
            const inner = (
              <>
                <img src={mod.image} alt="" />
                <div className="tc-home-card-copy">
                  <h2>{mod.title}</h2>
                  <p>{mod.text}</p>
                </div>
              </>
            );
            if (mod.to) {
              return (
                <Link key={mod.id} className="tc-home-card" to={isAuthenticated ? mod.to : '/login'}>
                  {inner}
                </Link>
              );
            }
            if (mod.sos) {
              return (
                <a key={mod.id} className="tc-home-card is-sos" href={mod.href} onClick={openSos}>
                  {inner}
                </a>
              );
            }
            if (mod.idle) {
              return (
                <div key={mod.id} className="tc-home-card is-idle">
                  {inner}
                </div>
              );
            }
            return (
              <a key={mod.id} className="tc-home-card" href={mod.href}>
                {inner}
              </a>
            );
          })}
        </div>

        <section className="tc-home-section">
          <h2>Featured attractions</h2>
          <p className="tc-home-lead">
            Highlights from the travel catalogue — open Itinerary to build a full day-by-day plan.
          </p>
          <div className="tc-home-attractions">
            {featured.map((item) => (
              <Link key={item.id || item.attraction_name} className="tc-home-attraction" to={itineraryTo}>
                <AttractionPhoto src={item.image} name={item.attraction_name} height={150} />
                <h3>{item.attraction_name}</h3>
                <span>{item.destination || item.category || 'Sri Lanka'}</span>
              </Link>
            ))}
          </div>
          {!featured.length && (
            <p className="tc-home-lead">Attractions load from the Tour Ceylon API when the backend is running.</p>
          )}
        </section>
      </div>
    </div>
  );
}
