import { useTranslation } from 'react-i18next';

export default function Footer() {
  const { t } = useTranslation();
  return (
    <footer>
      <div className="container">
        <div className="footer-head">
          <h2>{t('footer_title')}</h2>
          <div className="icons"></div>
        </div>
        <div className="footer-box">
          <FooterCard title={t('pricing_title')}
            ><ul>
              <li>{t('surgery')}</li>
              <li>{t('vet_treatment')}</li>
            </ul>
          </FooterCard>
          <FooterCard title={t('about_title')}
            ><ul>
              <li>{t('chat_with_us')}</li>
              <li>{t('doctors')}</li>
              <li>{t('contact_us')}</li>
            </ul>
          </FooterCard>
          <FooterCard title={t('pricing_title')}
            ><ul>
              <li>{t('surgery')}</li>
              <li>{t('vet_treatment')}</li>
            </ul>
          </FooterCard>
          <FooterCard title={t('about_title')}
            ><ul>
              <li>{t('chat_with_us')}</li>
              <li>{t('doctors')}</li>
              <li>{t('contact_us')}</li>
            </ul>
          </FooterCard>
        </div>
      </div>
    </footer>
  );
}
