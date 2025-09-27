import { useState } from "react";
import { Menu, X } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";

const pages = ["Home", "About", "Features","Tutorial"];

export default function Navbar() {
  const [navOpen, setNavOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleScroll = (id: string) => {
    if (location.pathname !== "/") {
      // Navigate to root page first
      navigate("/", { replace: false });
      // Wait a tick for the page to render
      setTimeout(() => {
        const element = document.getElementById(id);
        if (element) {
          element.scrollIntoView({ behavior: "smooth" });
        }
      }, 50);
    } else {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: "smooth" });
      }
    }

    setNavOpen(false); // close mobile menu
  };

  return (
    <nav className="sticky top-0 z-50 bg-[#F6F6F2] shadow">
      <div className="max-w-7xl mx-auto pl-2 pr-4 sm:pl-4 sm:pr-6 lg:pl-6 lg:pr-8">
        <div className="flex justify-start h-16 items-center">
          <div className="flex items-center">
            <span className="text-2xl font-bold tracking-widest text-[#1a237e] mr-2">
              <img src="/Profile.jpg" className="w-12 h-12 rounded-full object-cover" alt="Profile" />
            </span>

            {/* Desktop Links */}
            <div className="hidden md:flex space-x-6">
              {pages.map((page) => {
                let sectionId = page.toLowerCase() + "-section";
                return (
                  <button
                    key={page}
                    onClick={() => handleScroll(sectionId)}
                    className="uppercase tracking-wide text-[#1a237e] font-semibold text-lg px-3 py-2 rounded-md hover:underline hover:bg-[#040d2f]/90 hover:text-[#e5e4dd] transition"
                  >
                    {page}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setNavOpen(!navOpen)}
              className="text-[#1a237e] hover:text-[#040d2f]"
            >
              {navOpen ? <X size={28} /> : <Menu size={28} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav Menu */}
      {navOpen && (
        <div className="md:hidden bg-[#F6F6F2] px-4 pb-4 space-y-2">
          {pages.map((page) => {
            let sectionId = page.toLowerCase() + "-section";
            return (
              <button
                key={page}
                onClick={() => handleScroll(sectionId)}
                className="block uppercase tracking-wide text-[#1a237e] font-semibold text-lg px-3 py-2 rounded-md hover:underline hover:bg-[#040d2f]/90 hover:text-[#e5e4dd] transition"
              >
                {page}
              </button>
            );
          })}
        </div>
      )}
    </nav>
  );
}
