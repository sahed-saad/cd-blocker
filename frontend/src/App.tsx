import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import Navbar from "./components/Navbar"
import Home from "./pages/Home"
import Products from "./pages/Product"

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900">
        <Navbar /> {/* Navbar stays on top for all routes */}

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          
          {/* Add more routes as needed */}
        </Routes>
      </div>
    </Router>
  )
}

export default App
