import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from "./Pages/Home";
import Intelligrow from "./Pages/Intelligrow";
import SignUp from "./Pages/Signup";
import Login from "./Pages/auth/Login";
import Register from "./Pages/auth/Register";
import NotFoundPage from "./Pages/NotFoundPage"; // Import your NotFoundPage component

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/SignUp" element={<SignUp />} />
        <Route path="/Intelligrow" element={<Intelligrow />} />
        <Route path="/Login" element={<Login />} />
        <Route path="/Register" element={<Register/>}/>
        <Route path="*" element={<NotFoundPage />} /> {/* Handle unmatched routes */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
