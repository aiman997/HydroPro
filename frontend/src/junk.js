 {/* CART */}
 <div className="dropdown">
 <a className="dropdown-toggle" data-toggle="dropdown" aria-expanded="true">
     <FontAwesomeIcon icon={faShoppingCart} />
     <span>Your Cart</span>
     <div className="qty">3</div>
 </a>
 <Dropdown>
     <Dropdown.Toggle variant="success" id="dropdown-basic">
         <FontAwesomeIcon icon={faShoppingCart} />
         <span>Your Cart</span>
         <div className="qty">3</div>
     </Dropdown.Toggle>

     <Dropdown.Menu>
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
     </Dropdown.Menu>
 </Dropdown>
 <div className="menu-toggle">
     <a href="#">
         <FontAwesomeIcon icon={faBars} />
         <span>Menu</span>
     </a>
 </div>
</div>  