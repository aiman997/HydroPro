import './Header.css'
import React from 'react'
import WishCart from './WishCart'
import logo from '../Assets/Robectron.png';
import { Container, Row, Col, Dropdown } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

function Header() {
    return (
        <div id="header">
            <Container>
                <Row>
                    <Col md={3} className="clearfix">
                        <div className="header-logo">
                            <a href="#" className="logo">
                                <img src={logo} alt="" width="180" height="75" />
                            </a>
                        </div>
                    </Col>
                    <Col md={6} className="clearfix">
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
                    </Col>
                    <Col md={3} className="clearfix">
                        <WishCart />
                    </Col>
                </Row>
            </Container>
        </div>
  );
}

export default Header;
