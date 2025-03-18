import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import enTranslation from "./locales/en.json";
import deTranslation from "./locales/de.json";
import frTranslation from "./locales/fr.json";

i18n
  .use(initReactI18next)
  .init({
    resources: {
    en: { translation: enTranslation },
    de: { translation: deTranslation },
    fr: { translation: frTranslation }
    },
    lng: "en", // Default language
    fallbackLng: "en",
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;