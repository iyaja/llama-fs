import { MemoryRouter as Router, Routes, Route } from 'react-router-dom';
import MainScreen from './components/MainScreen';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainScreen />} />
      </Routes>
    </Router>
  );
}
