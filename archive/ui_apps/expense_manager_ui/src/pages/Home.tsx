import React from 'react';
import './Home.css';

interface HomeProps {
  onGetStarted: () => void;
}

const Home: React.FC<HomeProps> = ({ onGetStarted }) => {
  return (
    <div className="home-container">
      <h1 className="welcome-message">Welcome to your Expense Manager App</h1>
      <p className="description">
        Manage your expenses, track your spending, and stay on budget effortlessly.
        Take control of your finances with our intuitive and powerful tools.
      </p>
      <button className="get-started-button" onClick={onGetStarted}>
        Get Started
      </button>
    </div>
  );
};

export default Home;
