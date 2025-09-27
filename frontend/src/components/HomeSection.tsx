import { Link } from "react-router-dom";
import { useRef, useEffect, useState } from "react";

const HomeSection = () => {
  const sectionRef = useRef(null);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      if (sectionRef.current) {
        const rect = sectionRef.current.getBoundingClientRect();
        // Calculate scroll progress within the section (0 to 1)
        const progress = Math.max(0, Math.min(1, -rect.top / rect.height));
        setScrollY(progress);
      }
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll(); // Initial calculation

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Calculate transform values based on scroll progress
  const textTransform = `translateY(${scrollY * -50}px)`;
  const overlayOpacity = 0.5 + scrollY * 0.3; // Gets darker as we scroll

  return (
    <section
      ref={sectionRef}
      id="home-section"
      className="relative min-h-screen px-8 sm:px-16 flex items-start justify-end pt-16 sm:pt-20 md:pt-24 text-right bg-gray-900 bg-cover bg-center bg-no-repeat bg-fixed"
      style={{ backgroundImage: "url('/DataFabric.jpg')" }}
    >
      {/* Overlay that gets darker on scroll */}
      <div 
        className="absolute inset-0 bg-black transition-opacity duration-300"
        style={{ opacity: overlayOpacity }}
      ></div>

      <div 
        className="relative max-w-lg flex flex-col items-end gap-6 text-right text-white transition-transform duration-300"
        style={{ transform: textTransform }}
      >
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold whitespace-nowrap">
          Welcome to <span className="text-blue-600">CD Blocker</span>
        </h1>
        <p className="text-lg sm:text-xl leading-relaxed">
          CD Blocker helps keep your financial info safe while streaming or watching videos. With a few clicks, you can temporarily block your card to prevent unauthorized use or charges.
        </p>
        <Link to="/products">
          <button className="mt-4 px-6 py-3 text-lg font-bold rounded-lg bg-white text-[#11175d] shadow-md hover:bg-[#040d2f]/90 hover:text-white transform transition duration-150 hover:scale-105">
            TryNow!
          </button>
        </Link>
      </div>
    </section>
  );
}

export default HomeSection;