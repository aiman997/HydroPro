import React from 'react'
import NavBar from '../Components/NavBar/NavBar'
import TopHeader from '../Components/TopHeader/Top-Header';
import Slider from '../Components/Slider/Slider'
import Categories from '../Components/Categories/Categories';

const Home = () => {
  return (
    <div>
        <TopHeader/>
        <NavBar/>
        <Slider/>
        {/* <Categories/> */}
    </div>
  )
}

export default Home