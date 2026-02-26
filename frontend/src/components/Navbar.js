import React, { memo } from 'react';
import ThemeToggle from '../components/ThemeToggle';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Plane, LogOut, User } from 'lucide-react';

export default memo(function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav style={{
            position: 'sticky',
            top: 0,
            zIndex: 100,
            background: 'rgba(10, 10, 26, 0.85)',
            backdropFilter: 'blur(20px)',
            borderBottom: '1px solid var(--border)',
            padding: '0 24px',
        }}>
            <div style={{
                maxWidth: 1200,
                margin: '0 auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                height: 64,
            }}>
                {/* Logo */}
                <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{
                        width: 36,
                        height: 36,
                        borderRadius: 10,
                        background: 'var(--accent-gradient)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}>
                        <Plane size={20} color="white" />
                    </div>
                    <span style={{
                        fontSize: '1.2rem',
                        fontWeight: 800,
                        background: 'var(--accent-gradient)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        letterSpacing: '-0.02em',
                    }}>
                        Travel AI
                    </span>
                </Link>

                {/* Right side */}
                <ThemeToggle />
                {user ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        <Link to="/dashboard" className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
                            Dashboard
                        </Link>
                        <Link to="/generate" className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
                            New Trip
                        </Link>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                            <User size={16} />
                            <span>{user.full_name}</span>
                        </div>
                        <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '8px 12px' }} title="Logout">
                            <LogOut size={16} />
                        </button>
                    </div>
                ) : (
                    <div style={{ display: 'flex', gap: 8 }}>
                        <Link to="/login" className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>Log In</Link>
                        <Link to="/register" className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>Sign Up</Link>
                    </div>
                )}
            </div>
        </nav>
    );
}
