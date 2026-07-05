import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import de from './locales/de.json';
import en from './locales/en.json';
import es from './locales/es.json';
import fr from './locales/fr.json';
import it from './locales/it.json';
import ja from './locales/ja.json';
import ko from './locales/ko.json';
import nl from './locales/nl.json';
import pl from './locales/pl.json';
import pt from './locales/pt.json';
import ru from './locales/ru.json';
import sv from './locales/sv.json';
import tr from './locales/tr.json';
import uk from './locales/uk.json';
import zh from './locales/zh.json';

export const supportedLanguages = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'nl', label: 'Dutch', native: 'Nederlands' },
  { code: 'de', label: 'German', native: 'Deutsch' },
  { code: 'fr', label: 'French', native: 'Français' },
  { code: 'es', label: 'Spanish', native: 'Español' },
  { code: 'it', label: 'Italian', native: 'Italiano' },
  { code: 'pt', label: 'Portuguese', native: 'Português' },
  { code: 'pl', label: 'Polish', native: 'Polski' },
  { code: 'sv', label: 'Swedish', native: 'Svenska' },
  { code: 'ja', label: 'Japanese', native: '日本語' },
  { code: 'zh', label: 'Chinese', native: '简体中文' },
  { code: 'ko', label: 'Korean', native: '한국어' },
  { code: 'ru', label: 'Russian', native: 'Русский' },
  { code: 'tr', label: 'Turkish', native: 'Türkçe' },
  { code: 'uk', label: 'Ukrainian', native: 'Українська' },
];

const supportedCodes = supportedLanguages.map((lang) => lang.code);

const savedLanguage = localStorage.getItem('proxywake_language');
const browserLanguage = navigator.language?.split('-')[0];
const initialLanguage = savedLanguage || (supportedCodes.includes(browserLanguage) ? browserLanguage : 'en');

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    nl: { translation: nl },
    de: { translation: de },
    fr: { translation: fr },
    es: { translation: es },
    it: { translation: it },
    pt: { translation: pt },
    pl: { translation: pl },
    sv: { translation: sv },
    ja: { translation: ja },
    zh: { translation: zh },
    ko: { translation: ko },
    ru: { translation: ru },
    tr: { translation: tr },
    uk: { translation: uk },
  },
  lng: initialLanguage,
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export default i18n;

export const changeLanguage = async (language) => {
  const code = supportedCodes.includes(language) ? language : 'en';
  await i18n.changeLanguage(code);
  localStorage.setItem('proxywake_language', code);
  document.documentElement.lang = code;
};

document.documentElement.lang = initialLanguage;
