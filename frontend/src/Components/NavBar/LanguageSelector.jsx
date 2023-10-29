import React, { useState } from 'react';
import styled from 'styled-components';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import LanguageIcon from '@mui/icons-material/Language';
// Style for the LanguageSelector container
const LanguageSelectorContainer = styled.div`
  display: flex;
  align-items: center;
  position: relative;
  cursor: pointer;
`;

// Style for the Globe icon
const StyledGlobeIcon = styled(LanguageIcon)`
  font-size: 10px;
  margin-right: 8px;
`;

const StyledArrowIcon = styled(ArrowDropDownIcon)`
  font-size: 8px; // Adjust the size as needed
`;

// Style for the dropdown menu
const Dropdown = styled.div`
  position: absolute;
  top: 0%;
  right: 0;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  z-index: 1;
`;

// Style for each language item in the dropdown
const LanguageItem = styled.div`
  padding: 8px 16px;
  &:hover {
    background-color: #f0f0f0;
  }
`;

function LanguageSelector() {
  const [isOpen, setIsOpen] = useState(false);

  const languages = ['English', 'Spanish', 'French', 'German']; // Add more languages as needed

  return (
    <LanguageSelectorContainer
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <a href="#" style={{ color: '#FFF', textDecoration: 'none' }}></a>
      <StyledGlobeIcon />
      English
      <ArrowDropDownIcon style={{ marginLeft: '8px' }} />

      {isOpen && (
        <Dropdown>
          {languages.map((language) => (
            <LanguageItem key={language}>{language}</LanguageItem>
          ))}
        </Dropdown>
      )}
    </LanguageSelectorContainer>
  );
}

export default LanguageSelector;