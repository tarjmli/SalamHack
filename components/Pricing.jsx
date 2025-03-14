import PricingCard from "./PricingCard";

export default function Pricing() {
  return (
    <div className="pricing" id="pricing">
      <div className="container">
        <h2 className="title">{t('pricing_title')}</h2>
        <p>{t('pricing_description')}</p>
        <div className="pricing-box">
          <PricingCard type={"Free"} price={0} />
          <PricingCard type={"Starter"} price={8} />
          <PricingCard type={"Business"} price={16} isPopular={true} />
        </div>
      </div>
    </div>
  );
}