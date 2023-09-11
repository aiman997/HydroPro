import './Header.css'
import React from 'react'
import logo from './Robectron.png';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeart, faShoppingCart, faClose, faBars, faArrowCircleRight } from '@fortawesome/free-solid-svg-icons';
import { Container, Row, Col, Dropdown } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

function Dum() {
    return (
        <div className="container">
            <div className="row">
                <div className="col-md-3">
                    <div className="header-logo">
                        <a href="#" className="logo">
                            <img src={logo} alt="" width="180" height="75" />
                        </a>
                    </div>
                </div>
                {/* {SEARCH BAR} */}
                <div className="col-md-6">
                    <div className="header-search">
                        <form>
                            <select className="input-select">
                                <option value="0">All Categories</option>
                                <option value="1">Category 01</option>
                                <option value="1">Category 02</option>
                            </select>
                            <input className="input" placeholder="Search here" />
                            <button className="search-btn">Search</button>
                        </form>
                    </div>
                </div>
                {/* {ACCOUNT} */}  
                <div className="col-md-3 clearfix">
                    <div className="header-ctn">
                        {/* WISHLIST */}
                        <div>
                        <a href="#">
                            <FontAwesomeIcon icon={faHeart} />
                            <span>Your Wishlist</span>
                            <div className="qty">2</div>
                        </a>
                        </div>
                        {/* CART */}
                        <div className="dropdown">
                            <a className="dropdown-toggle" data-toggle="dropdown" aria-expanded="true">
                                <FontAwesomeIcon icon={faShoppingCart} />
                                <span>Your Cart</span>
                                <div className="qty">3</div>
                            </a>
                            <div className="cart-dropdown">
                                <div className="cart-list">
                                    <div className="product-widget">
                                        <div className="product-img">
                                            <img src="./product01.png" alt="" />
                                        </div>
                                        <div className="product-body">
                                            <h3 className="product-name"><a href="#">product name goes here</a></h3>
                                            <h4 className="product-price"><span className="qty">1x</span>$980.00</h4>
                                        </div>
                                        <button className="delete">
                                            <FontAwesomeIcon icon={faClose} />
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="product-widget">
                                <div className="product-img">
                                <img src="./product02.png" alt="" />
                                </div>
                                <div className="product-body">
                                <h3 className="product-name"><a href="#">product name goes here</a></h3>
                                <h4 className="product-price"><span className="qty">3x</span>$980.00</h4>
                                </div>
                                <button className="delete">
                                <FontAwesomeIcon icon={faClose} />
                                </button>
                            </div>
                            </div>
                            <div className="cart-summary">
                            <small>3 Item(s) selected</small>
                            <h5>SUBTOTAL: $2940.00</h5>
                            </div>
                            <div className="cart-btns">
                            <a href="#">View Cart</a>
                            <a href="#">Checkout  <FontAwesomeIcon icon={faArrowCircleRight} /></a>
                            </div>
                        </div>
                        </div>

                        <div className="menu-toggle">
                        <a href="#">
                            <FontAwesomeIcon icon={faBars} />
                            <span>Menu</span>
                        </a>
                        </div>
                    </div>
                </div>
  );
}

export default Dum;