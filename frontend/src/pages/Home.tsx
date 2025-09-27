import HomeSection from "../components/HomeSection"
import AboutSection from "../components/AboutSection"
import TutorialSection from "../components/TutorialSection"

export default function Home() {
  return (
    <div className="relative">
      <HomeSection />
      <AboutSection />
      <TutorialSection />
    </div>
  )
}
