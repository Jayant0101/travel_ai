import React, { Suspense, lazy, memo } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import ParticleBackground from './components/ParticleBackground';
import LoadingSpinner from './components/LoadingSpinner';
import { AnimatePresence, motion } from 'framer-motion';

// Lazy‑load page components for code‑splitting
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));
const LandingPage = lazy(() => import('./pages/LandingPage'));
const LoginPage = lazy(() => import('./pages/AuthPages').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('./pages/AuthPages').then(m => ({ default: m.RegisterPage })));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const GeneratePage = lazy(() => import('./pages/GeneratePage'));
const TripDetailPage = lazy(() => import('./pages/TripDetailPage'));


function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();
    if (loading) return <div className="loading-overlay"><div className="spinner" /></div>;
    return user ? children : <Navigate to="/login" />;
}

function AppRoutes() {
    const { user } = useAuth();
    const location = useLocation();

    return (
        <Suspense fallback={<LoadingSpinner />}>
            <Navbar />
            <AnimatePresence mode="wait">
                <Routes location={location} key={location.pathname}>
                    <Route path="/" element={<motion.div className="page" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}><LandingPage /></motion.div>} />
                    <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
                    <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <RegisterPage />} />
                    <Route path="/dashboard" element={<ProtectedRoute><motion.div className="page" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}><DashboardPage /></motion.div></ProtectedRoute>} />
                    <Route path="/generate" element={<ProtectedRoute><motion.div className="page" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}><GeneratePage /></motion.div></ProtectedRoute>} />
                    <Route path="/trip/:tripId" element={<ProtectedRoute><motion.div className="page" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}><TripDetailPage /></motion.div></ProtectedRoute>} />
                    <Route path="*" element={<NotFoundPage />} />
                </Routes>
            </AnimatePresence>
        </Suspense>
    );
}

export default function App() {
    return (
        <BrowserRouter>
            <ParticleBackground />
            <div className="gradient-orb gradient-orb-1" />
            <div className="gradient-orb gradient-orb-2" />
            <div className="gradient-orb gradient-orb-3" />
            <div className="grid-overlay" />
            <AuthProvider>
                <Toaster
                    position="top-right"
                    toastOptions={{
                        style: {
                            background: '#1a1a3a',
                            color: '#f0f0ff',
                            border: '1px solid rgba(255,255,255,0.08)',
                            borderRadius: '12px',
                            fontSize: '0.9rem',
                        },
                    }}
                />
                <AppRoutes />
            </AuthProvider>
        </BrowserRouter>
    );
}
