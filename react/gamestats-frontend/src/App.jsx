import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import RankingTable from './components/RankingTable';
import ItemAnalysis from './components/ItemAnalysis';
import SkillAnalysis from './components/SkillAnalysis';

function App() {
  return (
    <Router>
      <div className='min-h-screen bg-gray-100'>
        <Navbar />
        <div className='container mx-auto px-4 py-8'>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ranking" element={<RankingTable />} />
            <Route path="/items" element={<ItemAnalysis />} />
            <Route path="/skills" element={<SkillAnalysis />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;