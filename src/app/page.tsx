import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Install from "@/components/Install";
import PixelStrip from "@/components/PixelStrip";
import Features from "@/components/Features";
import InstallationGuide from "@/components/InstallationGuide";
import Documentation from "@/components/Documentation";

import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main>
      <Header />
      <Hero />
      <PixelStrip />
      <Install />
      <PixelStrip direction="down" />
      <Features/>
      <InstallationGuide />
      <Documentation />
      <FAQ />
      <Footer />
    </main>
  );
}
