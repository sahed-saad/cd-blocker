const TutorialSection = () => {
  return (
    <section
      id="tutorial-section"
      className="relative min-h-screen px-4 sm:px-8 bg-gradient-to-tr from-[#040d2f]/95 to-[#091c57]/92 text-white overflow-hidden flex flex-col items-center justify-start pt-24"
    >
      <div className="relative z-10 max-w-3xl w-full flex flex-col items-center gap-6 animate-[fadeInUp_0.6s_ease-out]">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-center bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent relative pb-2">
          Tutorial
        </h1>
        <p className="text-lg sm:text-xl text-center leading-relaxed">
          Here is our tutorial video.
        </p>

        {/* Video placeholder */}
        <div className="w-full max-w-2xl bg-white/5 rounded-xl p-8 flex items-center justify-center aspect-video border border-white/20 shadow-lg">
          <span className="text-white text-4xl select-none">▶</span>
        </div>

        {/* Optional steps section */}
        <div className="w-full max-w-2xl bg-white/8 backdrop-blur-md rounded-xl p-6 border border-white/10 shadow-lg mt-6">
          <ol className="list-none counter-reset-step space-y-3">
            <li className="relative pl-10 before:absolute before:left-0 before:top-0 before:w-8 before:h-8 before:flex before:items-center before:justify-center before:rounded-full before:bg-gradient-to-r from-blue-400 to-blue-700 before:text-white before:font-bold before:content-[counter(step)] counter-increment-step">
              Step 1: Start by connecting your account.
            </li>
            <li className="relative pl-10 before:absolute before:left-0 before:top-0 before:w-8 before:h-8 before:flex before:items-center before:justify-center before:rounded-full before:bg-gradient-to-r from-blue-400 to-blue-700 before:text-white before:font-bold before:content-[counter(step)] counter-increment-step">
              Step 2: Block your card with one click.
            </li>
            <li className="relative pl-10 before:absolute before:left-0 before:top-0 before:w-8 before:h-8 before:flex before:items-center before:justify-center before:rounded-full before:bg-gradient-to-r from-blue-400 to-blue-700 before:text-white before:font-bold before:content-[counter(step)] counter-increment-step">
              Step 3: Enjoy safe streaming.
            </li>
          </ol>
        </div>
      </div>
    </section>
  )
}

export default TutorialSection
