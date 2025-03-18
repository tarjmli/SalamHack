import Landing from "./Landing";
import Pricing from "./Pricing";
import Services from "./ServicesComp/Services";
import About from "./About";
import Footer from "./Footer";
import { useTranslation } from 'react-i18next';

export default function Main() {
  const { t } = useTranslation();
  return (
    <>
      <Landing />
      <Services />
      <Pricing />
      <About />
      <Footer />
    </>
  );
}