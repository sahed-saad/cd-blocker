import { useInView } from 'react-hook-inview';
const FeatureSection = () => {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  const features = [
    {
      title: "Real time video Streaming",
      description: "Real-time processing with less than 300ms latency for seamless streaming",
      icon: "⚡",
    },
    {
      title: "Precise Detection",
      description: "Advanced validation and format checkes ensures accuracy",
      icon: "🚀",
    },
    {
      title: "Streamlined Blurring",
      description: "Adjustable blur intensity to match your streaming preferences",
      icon: "🛡️",
    },
    {
      title: "Universal Campatibility",
      description: "Works seamlessly with Youtube, Twitch and any streaming paltform",
      icon: "👥",
    },
  ];

  return (
    <section
      id="features-section"
      className="relative min-h-screen flex items-center justify-center px-6 sm:px-12 bg-[#00092a] py-16"
    >
      <div className="max-w-6xl w-full flex flex-col lg:flex-row items-start lg:items-center gap-12">
        {/* Left Side: Main Title */}
        <div 
          ref={ref}
          className={`flex-1 transition-all duration-700 ${
            inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6">
            Take a closer look at the capabilities that set our platform apart.
          </h1>
          <p className="text-lg sm:text-xl text-white max-w-xl leading-relaxed">
            
            Explore the tools and functionalities that make our platform powerful and user-friendly.

          </p>
        </div>

        {/* Right Side: Features Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 flex-1">
          {features.map((feature, index) => (
            <div
              key={index}
              className={`bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl p-6 flex flex-col items-center text-center shadow-lg transition-all duration-700 delay-${index * 150} ${
                inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
              }`}
            >
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center mb-4">
                <span className="text-3xl">{feature.icon}</span>
              </div>
              <h3 className="text-xl sm:text-2xl font-bold text-[#070e31] mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-700 text-sm sm:text-base">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureSection;