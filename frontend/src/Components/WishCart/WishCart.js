import './WishCart.css'
import React from 'react'
import { Dropdown } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeart, faShoppingCart, faClose, faBars, faArrowCircleRight } from '@fortawesome/free-solid-svg-icons';
import 'bootstrap/dist/css/bootstrap.min.css';

function WishCart() {
    return(
        <div className="header-ctn">
            <div className='wishlist-container'>
                <a href="#" className = 'wishlist-link'>
                    <div className="qty" style={{ marginBottom: '8px' }}>2</div>
                    <div className="icon-container">
                        <FontAwesomeIcon icon={faHeart} />
                    </div>
                </a>
            </div> 
            <div>
                <span className="wishlist-text">Your Wishlist</span>
            </div>                         
        </div>
    );
}
export default WishCart;