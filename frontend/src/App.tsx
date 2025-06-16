import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LobbyPage from './pages/LobbyPage';
import GamePage from './pages/GamePage';
import './styles/main.css';
import './styles/HomePage.css';
import './styles/LobbyPage.css';
import './styles/GamePage.css';
import './styles/components.css';

function App() {
  return (
    <Router>
      <main className="app-container">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/lobby/:lobbyId" element={<LobbyPage />} />
          <Route path="/game/:gameId" element={<GamePage />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
