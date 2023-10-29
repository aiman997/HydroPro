import React from 'react';
import styled from 'styled-components';

// Replace the SVG import with the PNG import
import RobectronPng from '../../Assets/Robectron-V3/Verticle/Robectron_Transparent_Nobuffer.png';

const LogoContainer = styled.div`
    width: ${props => props.width || '300px'};
    height: ${props => props.height || '80px'};
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden; 
    position: relative;
`;

// Style the PNG image
const RobectronStyled = styled.img`
    position: absolute;
    top: 50%;  // center vertically
    left: 50%; // center it horizontally
    transform: translate(-50%, -50%); // Further ensure centering
    max-width: 150%;
    max-height: 100%;
`;

const PngLogo = ({ width, height }) => {
  return (
    <LogoContainer width={width} height={height}>
      <RobectronStyled src={RobectronPng} alt="Robectron Logo"/>
    </LogoContainer>
  );
}

export default PngLogo;