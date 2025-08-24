import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import PlanPage from './pages/PlanPage';
import DashboardHub from './pages/DashboardHub';
import ProfilePage from './pages/ProfilePage';
import HistoryPage from './pages/HistoryPage';
import { UserProvider } from './contexts/UserContext';

function App() {
  return (
    <UserProvider>
      <Router>
        <div className="page-wrapper">
          <Header />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/plan" element={<PlanPage />} />
            <Route path="/dashboard" element={<DashboardHub />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </div>
      </Router>
    </UserProvider>
  );
}

export default App;
