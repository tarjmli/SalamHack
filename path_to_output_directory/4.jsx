import { Link } from "react-router-dom";
import { useState, useContext } from "react";
import { UserContexts } from "../contexts/UserContexts";
import { useTranslation } from 'react-i18next';

export default function Navigator() {
  const { t } = useTranslation();
  const [path, setPath] = useState(window.location.pathname);
  const user = useContext(UserContexts);

  if (!window.localStorage.getItem("token")) {
    return (
      <ul className="navigation">
        <li>
          <a href="#services">{t('servicesLink')}</a>
        </li>
        <li>
          <a href="#about">{t('aboutLink')}</a>
        </li>
        <li>
          <a href="#pricing">{t('pricingLink')}</a>
        </li>
      </ul>
    );
  } else if (user.type === "Patient") {
    return (
      <ul className="navigation">
        <Link
          to=""
          onClick={() => {
            setPath("/");
          }}
        >
          <li className={path == "/" || path == "" ? "active" : ""}>{t('insightsLink')}</li>
        </Link>
        <Link
          to="chats"
          onClick={() => {
            setPath("chats");
          }}
        >
          <li className={path == "chats" ? "active" : ""}>{t('chatsLink')}</li>
        </Link>
        <Link
          to="/services"
          onClick={() => {
            setPath("services");
          }}
        >
          <li className={path == "services" ? "active" : ""}>{t('servicesLink')}</li>
        </Link>
      </ul>
    );
  } else {
    return (
      <ul className="navigation">
        <Link
          to=""
          onClick={() => {
            setPath("/");
          }}
        >
          <li className={path == "/" || path == "" ? "active" : ""}>{t('insightsLink')}</li>
        </Link>
        <Link
          to="/services"
          onClick={() => {
            setPath("services");
          }}
        >
          <li className={path == "services" ? "active" : ""}>{t('servicesLink')}</li>
        </Link>
        <li className={path == "profile" ? "active" : ""}>
          <a href="#">{t('profileLink')}</a>
        </li>
      </ul>
    );
  }
}