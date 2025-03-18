import { FaCheck } from "react-icons/fa6";
import { useTranslation } from "react-i18next";
export default function PricingCard({ type, price, isPopular }) {
  const { t } = useTranslation();
  return (
    <div className="pricing-card">
      {isPopular ? (
        <span className="popular-ticket">{t("mostPopular")}</span>
      ) : null}
      <div className="pricing-content">
        <h2>{type}</h2>
        <p>{t("bestForPersonalUse")}</p>
      </div>
      <p className="price">
        ${price}
        <span>
          <sub>/month</sub>
        </span>
      </p>
      <div>
        <h2>{price == 0 ? t("whatYouGet") : t("allFreeFeaturesPlus")}</h2>
        <ul className="pricing-list">
          <li>
            <FaCheck style={{ color: "rgb(0 95 255)", marginRight: "15px" }} />{" "}
            {t("taskManagement")}
          </li>
          <li>
            <FaCheck style={{ color: "rgb(0 95 255)", marginRight: "15px" }} />{" "}
            {t("projectPlanning")}
          </li>
          <li>
            <FaCheck style={{ color: "rgb(0 95 255)", marginRight: "15px" }} />{" "}
            {t("teamCollaboration")}
          </li>
          <li>
            <FaCheck style={{ color: "rgb(0 95 255)", marginRight: "15px" }} />{" "}
            {t("notificationAndReminders")}
          </li>
          <li>
            <FaCheck style={{ color: "rgb(0 95 255)", marginRight: "15px" }} />{" "}
            {t("whatYouGet")}
          </li>
        </ul>
      </div>
      <button className="start-btn">{t("getStarted")}</button>
    </div>
  );
}
