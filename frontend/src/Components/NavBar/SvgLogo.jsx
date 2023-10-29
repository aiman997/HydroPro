import React from 'react'
import styled, { keyframes } from 'styled-components';
import { ReactComponent as RobectronSvg } from '../../Assets/Robectron-V3/Verticle/Robectron_Transparent.svg'


const LogoContainer = styled.div`
    width: ${props => props.width || '200px'};
    height: ${props => props.height || '80px'};
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden; 
    position: relative;
`;

const RobectronStyled = styled(RobectronSvg)`
    position: absolute;
    top: 50%;  // This will center it vertically
    left: 50%; // This will center it horizontally
    transform: translate(-20%, -90%); // Further ensure centering
    max-width: 100%;
    max-height: 100%;
`;

const SvgLogo = ({ width, height }) => {
  return (
    <LogoContainer width={width} height={height}>
      <RobectronStyled/>
    </LogoContainer>
   
    )
}

export default SvgLogo


