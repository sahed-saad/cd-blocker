import HomeSection from "../components/HomeSection"
import AboutSection from "../components/AboutSection"
import TutorialSection from "../components/TutorialSection"
import Feature from  "../components/Feature"
export default function Home() {
  return (
    <div className="relative">
      <HomeSection />
      <AboutSection />
      <Feature />
      <TutorialSection />
    </div>
  )
}
