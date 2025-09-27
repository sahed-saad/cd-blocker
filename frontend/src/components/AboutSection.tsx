const AboutSection = () => {
  return (
    <section
      id="about-section"
      className="relative min-h-screen flex items-center justify-center px-4 sm:px-8 bg-[#00092a] overflow-hidden"
    >
      <div className="relative z-10 max-w-3xl w-full bg-white rounded-2xl border border-gray-200 shadow-lg p-10 flex flex-col items-center gap-6">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-center text-[#070e31] pb-4">
          About - CD Blocker
        </h1>
        <p className="text-lg sm:text-xl text-center leading-relaxed text-[#00092a]">
          CD Blocker was built with one mission: to give users peace of mind while streaming and multitasking online. We know that accidents and risks can happen — whether it’s a sudden unauthorized purchase or a distraction during a livestream.
        </p>
        <ul className="list-none w-full text-left space-y-2 text-lg sm:text-xl text-[#070e31]">
          <li className="relative pl-6 before:absolute before:left-0 before:top-0 before:text-[#070e31] before:content-['▸']">
            Instantly block or unblock your credit card.
          </li>
          <li className="relative pl-6 before:absolute before:left-0 before:top-0 before:text-[#070e31] before:content-['▸']">
            Prevent unauthorized transactions while you focus on your content.
          </li>
          <li className="relative pl-6 before:absolute before:left-0 before:top-0 before:text-[#070e31] before:content-['▸']">
            Enjoy streaming without financial worries.
          </li>
        </ul>
        <p className="text-center text-[#070e31] font-semibold bg-gray-50 p-4 rounded-lg border-l-4 border-[#070e31]  w-full">
          Our goal is to make online safety simple, fast, and reliable.
        </p>
      </div>
    </section>
  )
}

export default AboutSection
