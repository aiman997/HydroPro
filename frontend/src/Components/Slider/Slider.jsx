import React from 'react'
import KeyboardArrowRightOutlinedIcon from '@mui/icons-material/KeyboardArrowRightOutlined';
import KeyboardArrowLeftOutlinedIcon from '@mui/icons-material/KeyboardArrowLeftOutlined';
import styled from 'styled-components'
import { useState } from 'react';
import { sliderItems } from '../../data';


const Container = styled.div`
    width: 100%;
    height: 80vh;
    display: flex;
    /* background-color: #113e0d; */
    position: relative;
    overflow: hidden;
`;

const Arrow = styled.div`
    width: 50px;
    height: 50px;
    background-color: lightseagreen;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    bottom: 0;
    margin: auto;
    left: ${props => props.direction === "left" && "10px"};
    right: ${props => props.direction === "right" && "10px"};
    cursor: pointer;
    opacity: 0.5;
    z-index: 2;
`;

const Wrapper = styled.div`
    height: 100%;
    display: flex;
    transform: translateX(${props => props.slideIndex * -100}vw);
    transition: all 1.5s ease;
`;

const Slide = styled.div`
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    background-color: #${props=>props.bg};
`;

const ImgContainer = styled.div`
    flex: 1;
    height: 100%;
`;

const InfoContainer = styled.div`
    flex: 1;
    padding: 50px;
`;

const Image = styled.img`
    height: 80%;


`;

const Title = styled.div`
    font-size: 25px;
    font-weight: 500;
`;

const Desc = styled.p`
    margin: 50px 0px;
    font-size: 20px;
    font-weight: 400;
    letter-spacing: 3px;
`;
const Button = styled.button`
    padding: 10px 15px;
    font-size: 20px;
    background-color: transparent; //teal
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    outline: none;
`;
 
const Slider = () => {
    const [slideIndex, setSlideIndex] = useState(0);
    const handleClick = (direction) => {
        if (direction === "left") {
            setSlideIndex(slideIndex > 0 ? slideIndex - 1 : 2); // Adjust number based on your total slides
        } else {
            setSlideIndex(slideIndex < 2 ? slideIndex + 1 : 0); // Adjust number based on your total slides
        }
    };
  return (
    <Container>
        <Arrow direction="left" onClick = {() => handleClick("left")}>
            <KeyboardArrowLeftOutlinedIcon/>
        </Arrow>
        <Wrapper slideIndex = {slideIndex}>
            {sliderItems.map((item) => (
                <Slide bg={item.bg}>
                <ImgContainer>
                    <Image src={item.img}/>
                </ImgContainer>
                <InfoContainer>
                    <Title>
                        {item.title}
                    </Title>
                    <Desc>
                        {item.desc}
                    </Desc>
                    <Button>
                        Get Now
                    </Button>
                </InfoContainer>
            </Slide>

            ))}
        </Wrapper>
        <Arrow direction = "right" onClick = {() => handleClick("right")}>
            <KeyboardArrowRightOutlinedIcon/>
        </Arrow>
    </Container>
  )
}

export default Slider