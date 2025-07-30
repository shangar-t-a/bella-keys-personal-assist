import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import DashboardList from './pages/DashboardList';
import SpendingAccountSummary from './pages/SpendingAccountSummary'; // Import the new component
import './App.css';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('darkMode');
    return savedMode ? JSON.parse(savedMode) : false;
  });

  useEffect(() => {
    document.body.classList.toggle('dark-mode', isDarkMode);
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode((prevMode: boolean) => !prevMode);
  };

  const navigate = useNavigate();

  const handleGetStarted = () => {
    console.log('Navigating to Dashboard List');
    navigate('/dashboard');
  };

  return (
    <div className="app-container">
      <Header appName="Expense Manager" onToggleDarkMode={toggleDarkMode} isDarkMode={isDarkMode} />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home onGetStarted={handleGetStarted} />} />
          <Route path="/dashboard" element={<DashboardList />} />
          <Route path="/dashboard/spending-account-summary" element={<SpendingAccountSummary />} />
        </Routes>
      </main>
      <Footer copyrightText="© 2025 Shangar Arivazhagan" />
    </div>
  );
}

export default App;
