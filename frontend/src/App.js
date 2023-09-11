import "./App.css";
import Footer from "./Footer";
import MainContent from "./MainContent";
import TopHeader from "./Top-Header";
import Header from "./Header";

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