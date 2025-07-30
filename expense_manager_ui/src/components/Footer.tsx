import React from 'react';
import './Footer.css';

interface FooterProps {
  copyrightText: string;
}

const Footer: React.FC<FooterProps> = ({ copyrightText }) => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>{copyrightText}</p>
      </div>
    </footer>
  );
};

export default Footer;
