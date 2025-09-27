import "./home.css";
const Home = () => {
  return (
    <div className="home-container">
      <div className="home-header">
        <h1 className="home-title">
          Welcome to <span className="cd-blocker">CD Blocker</span>
        </h1>
        <p className="home-description">
          CD Blocker helps keep your financial info safe while streaming or watching videos. With a few clicks, you can temporarily block your card to prevent unauthorized use or charges.
        </p>
        <a href="http://localhost:5000/" target="_blank" rel="noopener noreferrer">
          <button className="home-button">TryNow!</button>
        </a>
      </div>
        
    </div>
  );
};

export default Home;
