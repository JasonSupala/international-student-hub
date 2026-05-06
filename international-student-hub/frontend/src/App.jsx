import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Checklist from './pages/Checklist'
import ChecklistItemDetail from './pages/ChecklistItemDetail'
import Directory from './pages/Directory'
import DirectoryEntryDetail from './pages/DirectoryEntryDetail'
import Community from './pages/Community'
import PostDetail from './pages/PostDetail'
import Profile from './pages/Profile'
import AdminPanel from './pages/AdminPanel'

// Protect routes that require login
function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading-center"><div className="spinner" /></div>
  return user ? children : <Navigate to="/login" replace />
}

function SuperuserRoute({ children }) {
  const { user, isSuperuser, loading } = useAuth()
  if (loading) return <div className="loading-center"><div className="spinner" /></div>
  if (!user) return <Navigate to="/login" replace />
  return isSuperuser ? children : <Navigate to="/" replace />
}

function AppRoutes() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/"           element={<Home />} />
        <Route path="/login"      element={<Login />} />
        <Route path="/register"   element={<Register />} />
        <Route path="/checklist"  element={<PrivateRoute><Checklist /></PrivateRoute>} />
        <Route path="/checklist/items/:slug" element={<PrivateRoute><ChecklistItemDetail /></PrivateRoute>} />
        <Route path="/directory"  element={<Directory />} />
        <Route path="/directory/entries/:slug" element={<DirectoryEntryDetail />} />
        <Route path="/community"  element={<Community />} />
        <Route path="/community/:id" element={<PostDetail />} />
        <Route path="/profile"    element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="/admin-panel" element={<SuperuserRoute><AdminPanel /></SuperuserRoute>} />
        <Route path="*"           element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
