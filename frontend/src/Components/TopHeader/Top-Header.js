import styled from 'styled-components';
import PhoneIcon from '@mui/icons-material/Phone';
import EmailIcon from '@mui/icons-material/Email';
import PlaceIcon from '@mui/icons-material/Place';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LanguageSelector from '../NavBar/LanguageSelector'

const Container = styled.div`
    padding-right: 15px;
    display: flex;
    justify-content: space-between;
    text-align: center;
`;

const TopHeaderContainer = styled.div`
    height: 30px;
    background-color: #003B04; 
    /* 1E1F29 */
`;

const HeaderLinks = styled.ul`

    display: flex;
    align-items: center;

    li {
        display: inline-block;
        margin-right: 20px;
        font-size: 11px;

        &:last-child {
            margin-right: 0px;
        }

        a {
            color: #FFF;
            text-decoration: none;

            .icon-style {
                /* color: #D10024;  A6C4B1 #B2D89D #B2EF9D*/ 
                color: #A0FF67;
                margin-right: 3px;
                font-size: 16px;
            }
            &:hover {
                color: #A0FF67;
            }
        }
    }
`;


const LinkItem = ({ icon, label, href }) => (
    <li>
        <a href={href || "#"}>
            {icon && <span className="icon-style">{icon}</span>}
            {label}
        </a>
    </li>
);

const TopHeader = () => {
    const leftLinks = [
        { icon: <PhoneIcon className="icon-style" />, label: "+089-481-7366" },
        { icon: <EmailIcon className="icon-style" />, label: "info@robectron.com" },
        { icon: <PlaceIcon className="icon-style" />, label: "Roebuck Road Dublin 14" }
    ];

    const rightLinks = [
        { icon: null, children: <LanguageSelector /> },
        { icon: <AttachMoneyIcon className="icon-style" />, label: "USD" },
        { icon: <AccountCircleIcon className="icon-style" />, label: "My Account" }
    ];

    return (
        <TopHeaderContainer>
            <Container>
                <HeaderLinks>
                    {leftLinks.map((link, index) => 
                        <LinkItem key={index} {...link} />
                    )}
                </HeaderLinks>
                <HeaderLinks>
                    {rightLinks.map((link, index) => 
                        <LinkItem key={index} {...link} />
                    )}
                </HeaderLinks>
            </Container>
        </TopHeaderContainer>
    );
};

export default TopHeader;