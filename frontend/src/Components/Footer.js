import React from 'react';
import './Footer.css';

function Footer() {
  return (
    <div className="footer-container">
        <div className="footer-column">
            <h4>ABOUT US</h4>
            <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut.</p>
            <p>1734 Stonecoal Road</p>
            <p>+021-95-51-84</p>
            <p>email@email.com</p>
        </div>
        
        <div className="footer-column">
            <h4>CATEGORIES</h4>
            <ul>
                <li>Hot deals</li>
                <li>Laptops</li>
                <li>Smartphones</li>
                <li>Cameras</li>
                <li>Accessories</li>
            </ul>
        </div>
      
        <div className="footer-column">
            <h4>INFORMATION</h4>
            <ul>
                <li>About Us</li>
                <li>Contact Us</li>
                <li>Privacy Policy</li>
                <li>Orders and Returns</li>
                <li>Terms & Conditions</li>
            </ul>
        </div>
        
        <div className="footer-column">
            <h4>SERVICE</h4>
            <ul>
                <li>My Account</li>
                <li>View Cart</li>
                <li>Wishlist</li>
                <li>Track My Order</li>
                <li>Help</li>
            </ul>
        </div>
    </div>
  );
}

export default Footer;
