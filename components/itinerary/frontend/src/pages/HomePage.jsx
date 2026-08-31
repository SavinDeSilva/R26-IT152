import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { attractionsApi } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { SITES } from '@shared/config';
import { useSiteI18n } from '@shared/i18n/react';
import AttractionPhoto from '../components/AttractionPhoto';
import { attractionLabels } from '../utils/attractionLabels';
import { seedAttractionsCatalog, writeAttractionsCatalogCache } from '../utils/attractionsCatalog';
import { openSosDashboard } from '../api/sosClient';

const MODULES = [
  {
    id: 'itinerary',
    titleKey: 'moduleItinerary',
    textKey: 'moduleItineraryDesc',
    image: '/itinerary.webp',
    to: '/attractions',
  },
  {
    id: 'wellness',
    titleKey: 'moduleWellness',
    textKey: 'moduleWellnessDesc',
    image: '/wellness.jpeg',
    href: SITES.wellness,
  },
  {
    id: 'sos',
    titleKey: 'moduleSos',
    textKey: 'moduleSosDesc',
    image: '/sos.jpeg',
    href: `${String(SITES.sos || '').replace(/\/$/, '')}/enter?next=/home`,
    sos: true,
  },
  {
    id: 'livedata',
    titleKey: 'moduleLiveData',
    textKey: 'moduleLiveDataDesc',
    image: '/images.jpeg',
    href: SITES.livedata,
  },
];

export default function HomePage() {
  const { t } = useSiteI18n();
  const { isAuthenticated } = useAuth();
  const [attractions, setAttractions] = useState(() => seedAttractionsCatalog([]));

  useEffect(() => {
    let cancelled = false;
    attractionsApi
      .list()
      .then(({ data }) => {
        if (cancelled) return;
        const list = data?.attractions || [];
        const withPhotos = list.filter((a) => a.image);
        const featured = (withPhotos.length >= 8 ? withPhotos : list).slice(0, 8);
        setAttractions(featured);
        if (list.length) writeAttractionsCatalogCache(list);
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
          <p className="tc-home-kicker">{t('homeHeroBadge')}</p>
          <h1>{t('homeHeroTitle')}</h1>
          <p>{t('homeHeroDesc')}</p>
          <Link className="tc-home-cta" to={itineraryTo}>
            {t('planTrip')}
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
                  <h2>{t(mod.titleKey)}</h2>
                  <p>{t(mod.textKey)}</p>
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
          <h2>{t('featuredAttractions')}</h2>
          <p className="tc-home-lead">
            {t('featuredAttractionsLead')}
          </p>
          <div className="tc-home-attractions">
            {featured.map((item) => {
              const labels = attractionLabels(item, t);
              return (
              <Link key={item.id || item.attraction_name} className="tc-home-attraction" to={itineraryTo}>
                <AttractionPhoto src={item.image} name={item.attraction_name} height={150} />
                <h3>{item.attraction_name}</h3>
                <span>{item.destination || labels.category || item.category || t('sriLanka')}</span>
              </Link>
              );
            })}
          </div>
          {!featured.length && (
            <p className="tc-home-lead">{t('attractionsLoadHint')}</p>
          )}
        </section>
      </div>
    </div>
  );
}
