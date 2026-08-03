import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { AnimatedBackground, MouseGlow } from "@/components/landing/animated-background";
import {
  AgentShowcase,
  Faq,
  FeatureCards,
  Hero,
  HowItWorks,
  Stats,
  Testimonials,
} from "@/components/landing/landing-sections";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-background">
      <AnimatedBackground />
      <MouseGlow />
      <div className="relative z-10">
        <Navbar />
        <main>
          <Hero />
          <FeatureCards />
          <HowItWorks />
          <AgentShowcase />
          <Stats />
          <Testimonials />
          <Faq />
        </main>
        <Footer />
      </div>
    </div>
  );
}
