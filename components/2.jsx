import { GoArrowUpRight } from "react-icons/go";
import { useTranslation } from "react-i18next";
export default function Landing() {
  const { t } = useTranslation();
  return (
    <main>
      <div className="container main">
        <div className="main-content">
          <h1>{t("landingPageTitle")}</h1>
          <p>{t("landingPageDescription")}</p>
          <button>
            {t("submitButton")} <GoArrowUpRight style={{ marginLeft: "5px" }} />
          </button>
          <img
            className="watch-img"
            src="./watch.png"
            alt={t("watchImageAlt")}
            onLoad={(e) => {
              e.target.classList.add("animationWatch");
            }}
          />
        </div>
        <div className="image">
          <img src="./landingImg.png" alt={t("landingImageAlt")} />
          <p>{t("trackYourHealthEffectively")}</p>
          <p>{t("gainInsightsIntoYourHealthData")}</p>
        </div>
      </div>
      <img
        className="watch-img"
        src="./watch.png"
        alt={t("watchImageAlt")}
        onLoad={(e) => {
          e.target.classList.add("animationWatch");
        }}
      />
    </main>
  );
}
