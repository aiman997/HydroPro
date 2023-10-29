import styled from 'styled-components'
import Badge from '@mui/material/Badge';
import ShoppingCartOutlinedIcon from '@mui/icons-material/ShoppingCartOutlined';
import FavoriteBorderTwoToneIcon from '@mui/icons-material/FavoriteBorderTwoTone';
import PngLogo from './PngLogo';
import DropdownSearch from './DropdownSearch';



const Container = styled.div `
    height: 60px;
`;

const Wrapper = styled.div`
    background-color: #0e734a;
    padding: 2px 20px;
    display: flex;
    justify-content: space-between;
`;

const Left = styled.div`
    flex: 1;
    align-items: center;
    display: flex;
   
`;
const Center = styled.div`
    flex: 2;
    display: flex;
    align-items: center;
    justify-content: center;
`;

const Right = styled.div`
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: flex-end;
` ;

const SearchContainer = styled.div`
    display: flex;
    align-items: center;
    margin-left: 15px;
    width: 100%;
    height: 30px;
  
`;

const Logo = styled.div`
    width: 100px;
    height: 60px;
    display: flex;
    overflow: hidden;
    align-items: center;
    justify-content: center;
    margin-left: -20px;
`;


const MenuItem = styled.div`
    font-size: 14px;
    align-items: center;
    margin-left: 25px;
    cursor: pointer;
`;

const NavBar = () => {
  return (
    <Container>
        <Wrapper>
            <Left>
                <Logo>
                    {/* <MpLogo/> */}
                    {/* <AnimatedLogo width="500px" height="500px"/> */}
                    <PngLogo width="100px" height="60px"/>
                </Logo>
            </Left>
            <Center>
                <SearchContainer>
                    <DropdownSearch/>
                </SearchContainer> 
            </Center>
            <Right>
                <MenuItem>
                    <Badge badgeContent={4} color="secondary">
                        <FavoriteBorderTwoToneIcon color="action"/>
                    </Badge>
                </MenuItem>
                <MenuItem>
                    <Badge badgeContent={2} color="primary">
                        <ShoppingCartOutlinedIcon color="action"/>
                    </Badge>
                </MenuItem>
                <MenuItem>IntelliGrow</MenuItem>
            </Right>
        </Wrapper>
    </Container>
  )
}

export default NavBar