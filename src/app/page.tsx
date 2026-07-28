import dynamic from 'next/dynamic';
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import PixelStrip from "@/components/PixelStrip";

const Install = dynamic(() => import("@/components/Install"));
const Features = dynamic(() => import("@/components/Features"));
const InstallationGuide = dynamic(() => import("@/components/InstallationGuide"));
const Documentation = dynamic(() => import("@/components/Documentation"));
const FAQ = dynamic(() => import("@/components/FAQ"));
const Footer = dynamic(() => import("@/components/Footer"));

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
