import { Navigate, Route, Routes } from 'react-router-dom'

import { StatusPage } from '../pages/StatusPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<StatusPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

