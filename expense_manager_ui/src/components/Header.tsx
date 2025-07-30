import React from 'react';
import { Link } from 'react-router-dom';
import { Sun, Moon } from 'lucide-react'; // Import icons
import './Header.css';

interface HeaderProps {
  appName: string;
  onToggleDarkMode: () => void;
  isDarkMode: boolean;
}

const Header: React.FC<HeaderProps> = ({ appName, onToggleDarkMode, isDarkMode }) => {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="app-name-link">
          <h1>{appName}</h1>
        </Link>
        <button onClick={onToggleDarkMode} className="dark-mode-toggle" aria-label={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
    </header>
  );
};

export default Header;
