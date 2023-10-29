import React from 'react'
import styled from 'styled-components';


const VideoContainer = styled.div`
  width: 100%; // replace with your actual desired width: ;
  height: 100%; // replace with your actual desired height
  overflow: hidden;
  position: relative;
`;

// Video element styles
const StyledVideo = styled.video`
  width: 100%;
  height: auto;
  position: absolute;
  top: 50%;
  left: 80%;
  transform: translate(-80%, -50%) scale(0.4); // Center the video and then scale
`;

const MpLogo = () => {
  return (
    <VideoContainer>
      <StyledVideo autoPlay muted> {/* autoPlay loop muted */}
        <source src={`${process.env.PUBLIC_URL}/Robectron.mp4`} type="video/mp4" />
        Your browser does not support the video tag.
      </StyledVideo>
    </VideoContainer>
  );
}

export default MpLogo


// (logo background #183309)