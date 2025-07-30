import React from 'react';
import { useNavigate } from 'react-router-dom';
import './DashboardList.css';

interface DashboardCardProps {
  name: string;
  description: string;
  path: string;
}

const DashboardCard: React.FC<DashboardCardProps> = ({ name, description, path }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(path);
  };

  return (
    <div className="dashboard-card" onClick={handleClick}>
      <h2 className="dashboard-card-name">{name}</h2>
      <p className="dashboard-card-description">{description}</p>
    </div>
  );
};

const DashboardList: React.FC = () => {
  const dashboards = [
    {
      name: 'Spending Account Summary',
      description: 'Track your monthly spending across different accounts',
      path: '/dashboard/spending-account-summary',
    },
    // Only include dashboards explicitly defined in requirements/pages/dashboard-list-page.md
  ];

  return (
    <div className="dashboard-list-container">
      <h1 className="dashboard-list-title">Available Dashboards</h1>
      <div className="dashboard-cards-grid">
        {dashboards.map((dashboard) => (
          <DashboardCard
            key={dashboard.name}
            name={dashboard.name}
            description={dashboard.description}
            path={dashboard.path}
          />
        ))}
      </div>
    </div>
  );
};

export default DashboardList;
