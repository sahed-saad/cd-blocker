import { Link } from "react-router-dom";

const HomeSection = () => {
  return (
    <section
      id="home-section"
      className="relative min-h-screen px-8 sm:px-16 flex items-start justify-center pt-32 sm:pt-40 md:pt-48 text-center bg-gray-900 bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: "url('/DataFabric.jpg')" }}
    >
      {/* Optional overlay for better text readability */}
      <div className="absolute inset-0 bg-opacity-50"></div>

      <div className="relative max-w-lg flex flex-col items-center gap-6 text-center text-white">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold">
          Welcome to <span className="text-blue-400">CD Blocker</span>
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
};

export default HomeSection;
