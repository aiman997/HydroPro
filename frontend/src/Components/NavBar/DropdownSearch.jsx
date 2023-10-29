import React, { useState } from 'react';
import styled from 'styled-components';
import SearchIcon from '@mui/icons-material/Search';

const SearchContainer = styled.div`
    display: flex;
    align-items: center;
    border: 1px solid #ccc;
    height: 100%;
    width: 100%;
    font-family: Arial, sans-serif;
    background-color: #f5f5f5;
    border-radius: 4px;
`;

const DropdownContainer = styled.div`
    display: flex;
    align-items: center;
    background-color: #4CAF50;
    cursor: pointer;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    height: 100%;
`;

const DropdownLabel = styled.div`
    height: 100%;
    background-color: #ef8433;
    color: #fff;
`;

const DropdownArrow = styled.div`
    background-color: #4CAF50;
    color: #fff;
`;

const SearchInput = styled.input`
    flex: 1;
    padding: 1px;
    border: none;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    outline: none;
`;

const SearchIconContainer = styled.div`
    background-color: #fcb10e;
    border-radius: 5px;
    margin-right: 3px; 

`;

const DropdownSearch = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <SearchContainer>
            <SearchInput placeholder="Keyword / Part #" />
            <SearchIconContainer>
                <SearchIcon/>
            </SearchIconContainer>
        </SearchContainer>
    );
}

export default DropdownSearch;
