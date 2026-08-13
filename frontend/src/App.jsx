import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Home from './pages/Home'
import FarmDetails from './pages/FarmDetails'
import SoilTest from './pages/SoilTest'
import Environment from './pages/Environment'
import Analysis from './pages/Analysis'
import Recommendations from './pages/Recommendations'
import CropDetails from './pages/CropDetails'
import IWantToGrow from './pages/IWantToGrow'
import WhatIf from './pages/WhatIf'
import Dashboard from './pages/Dashboard'

// Global state context
import { AppProvider } from './context/AppContext'

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/farm-details" element={<FarmDetails />} />
          <Route path="/soil-test" element={<SoilTest />} />
          <Route path="/environment" element={<Environment />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/crop/:cropName" element={<CropDetails />} />
          <Route path="/i-want-to-grow" element={<IWantToGrow />} />
          <Route path="/what-if" element={<WhatIf />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  )
}
