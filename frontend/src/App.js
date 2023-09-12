import "./App.css";
import Footer from "./Components/Footer";
import MainContent from "./Components/MainContent";
import TopHeader from "./Components/Top-Header";
import Header from "./Components/Header";

function App() {
  return (
    <div className="App">
      <TopHeader/>
      <Header/>
      <MainContent />
      <Footer />
    </div>
  );
}

export default App;