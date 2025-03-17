import { useState } from "react";
import { useTranslation } from 'react-i18next';

export default function About() {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(true);
  const [isOpenSecond, setIsOpenSecond] = useState(false);
  return (
    <div className="about" id="about">
      <div className="container">
        <h2 className="title">{t('aboutTitle')}</h2>
        <p>
          {t('aboutDescription')}
        </p>
        <div className="about-content">
          <div className="accordion">
            <span onClick={() => setIsOpen(!isOpen)}></span>
            <div></div>
            <ul
              style={{
                height: isOpen ? "100px" : "0px",
                overflow: "hidden",
                transition: "0.7s",
              }}
            >
              <li>
                <h3>{t('whatIsMourafik')}</h3>
                <p style={{ lineHeight: "1.5" }}>
                  {t('mourafikDescription')}
                </p>
              </li>
              <li>
                <h3>{t('ourGoals')}</h3>
                <p style={{ lineHeight: "1.5" }}>
                  {t('mourafikDescription')}
                </p>
              </li>
            </ul>
          </div>
          <div className="accordion">
            <span onClick={() => setIsOpenSecond(!isOpenSecond)}></span>
            <div></div>
            <h2 style={{ padding: "10px 0" }}>{t('doctorListTitle')}</h2>
            <div className="list-doctor"></div>
          </div>
        </div>
      </div>
    </div>
  );
}