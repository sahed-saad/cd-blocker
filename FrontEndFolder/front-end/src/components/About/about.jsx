import "./about.css";

const About = () => {
  return (
    <section className="about-section" id="about-section">
      <div className="about-container">
        <h1 className="about-title">About - CD Blocker</h1>
        <p className="about-description">
          CD Blocker was built with one mission: to give users peace of mind while streaming and multitasking online. We know that accidents and risks can happen — whether it’s a sudden unauthorized purchase or a distraction during a livestream.
        </p>
        <ul className="about-list">
          <li>Instantly block or unblock your credit card.</li>
          <li>Prevent unauthorized transactions while you focus on your content.</li>
          <li>Enjoy streaming without financial worries.</li>
        </ul>
        <p className="about-goal">
          Our goal is to make online safety simple, fast, and reliable.
        </p>
      </div>
    </section>
  );
};

export default About;
