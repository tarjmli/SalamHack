import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import enTranslation from "./locales/en.json";
import arTranslation from "./locales/ar.json";
import frTranslation from "./locales/fr.json";

i18n
  .use(initReactI18next)
  .init({
    resources: {
    en: { translation: enTranslation },
    ar: { translation: arTranslation },
    fr: { translation: frTranslation }
    },
    lng: "en", // Default language
    fallbackLng: "en",
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;