import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPhone, faEnvelope, faMapMarker, faDollarSign, faUser } from '@fortawesome/free-solid-svg-icons';
import './Top-Header.css';

function TopHeader() {
  return (
    <div id="top-header">
      <div className="container">
        <ul className="header-links pull-left">
          <li><a href="#"><FontAwesomeIcon className="icon-style" icon={faPhone} /> +089-481-7366</a></li>
          <li><a href="#"><FontAwesomeIcon className="icon-style" icon={faEnvelope} /> info@robectron.com</a></li>
          <li><a href="#"><FontAwesomeIcon className="icon-style" icon={faMapMarker} /> Roebuck Road Dublin 14</a></li>
        </ul>
        <ul className="header-links pull-right">
          <li><a href="#"><FontAwesomeIcon className="icon-style" icon={faDollarSign} /> USD</a></li>
          <li><a href="#"><FontAwesomeIcon className="icon-style" icon={faUser} /> My Account</a></li>
        </ul>
      </div>
    </div>
  );
}

export default TopHeader;
