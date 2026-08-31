import { uiKey } from '@shared/i18n/uiKey';

/** Localized category / mood labels (catalog text comes translated from the API). */
export function attractionLabels(attraction, t) {
  const category = (attraction?.category || '').trim();
  const mood = (attraction?.mood_tag || '').trim();
  return {
    category: category ? t(uiKey('cat', category)) : '',
    mood: mood ? t(uiKey('mood', mood)) : '',
  };
}
