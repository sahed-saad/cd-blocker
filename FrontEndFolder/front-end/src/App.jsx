import './App.css';
import ResponsiveAppBar from './components/Navbar/narbar';
import Home from './components/Home/home';
import About from './components/About/about';
import Tutorial from './components/Tutorial/tutorial';
const App = () => {

  return (
    <div className="App">
      <ResponsiveAppBar />
      <div className='main-content'>
        <section id="home-section"><Home /></section>
        <section id="about-section"><About /></section>
        <section id="tutorial-section"><Tutorial /></section>
      </div>
    </div>
  )
}

export default App