import FooterCard from "./FooterCard";
import { useTranslation } from 'react-i18next';

export default function Footer() {
  const { t } = useTranslation();
  return (
    <footer>
      <div className="container">
        <div className="footer-head">
          <h2>{t('title')}</h2>
          <div className="icons"></div>
        </div>
        <div className="footer-box">
          <FooterCard title={t('pricing')}>
            <ul>
              <li>{t('surgery')}</li>
              <li>{t('vetTreatment')}</li>
            </ul>
          </FooterCard>
          <FooterCard title={t('about')}>
            <ul>
              <li>{t('chatWithUs')}</li>
              <li>{t('doctors')}</li>
              <li>{t('contactUs')}</li>
            </ul>
          </FooterCard>
          <FooterCard title={t('pricing')}>
            <ul>
              <li>{t('surgery')}</li>
              <li>{t('vetTreatment')}</li>
            </ul>
          </FooterCard>
          <FooterCard title={t('about')}>
            <ul>
              <li>{t('chatWithUs')}</li>
              <li>{t('doctors')}</li>
              <li>{t('contactUs')}</li>
            </ul>
          </FooterCard>
        </div>
      </div>
    </footer>
  );
}