import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import nl from './locales/nl.json';
import de from './locales/de.json';
import fr from './locales/fr.json';

const savedLanguage = localStorage.getItem('proxywake_language');
const browserLanguage = navigator.language?.split('-')[0];
const supported = ['en', 'nl', 'de', 'fr'];
const initialLanguage = savedLanguage || (supported.includes(browserLanguage) ? browserLanguage : 'en');

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    nl: { translation: nl },
    de: { translation: de },
    fr: { translation: fr },
  },
  lng: initialLanguage,
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export default i18n;

export const supportedLanguages = [
  { code: 'en', label: 'English' },
  { code: 'nl', label: 'Nederlands' },
  { code: 'de', label: 'Deutsch' },
  { code: 'fr', label: 'Français' },
];

export const changeLanguage = async (language) => {
  await i18n.changeLanguage(language);
  localStorage.setItem('proxywake_language', language);
  document.documentElement.lang = language;
};

document.documentElement.lang = initialLanguage;
