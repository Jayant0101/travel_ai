import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { Plane, Mail, Lock, User, Phone, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await login(email, password);
            toast.success('Welcome back!');
            navigate('/dashboard');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="glass-card"
                style={{ width: '100%', maxWidth: 440, padding: 40 }}
            >
                {/* Header */}
                <div style={{ textAlign: 'center', marginBottom: 32 }}>
                    <div style={{
                        width: 56, height: 56, borderRadius: 16,
                        background: 'var(--accent-gradient)',
                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                        marginBottom: 16, boxShadow: '0 0 40px rgba(108, 92, 231, 0.3)',
                    }}>
                        <Plane size={28} color="white" />
                    </div>
                    <h1 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: 8 }}>Welcome Back</h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Sign in to plan your next adventure</p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                    <div className="input-group">
                        <label htmlFor="login-email">Email</label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input id="login-email" type="email" className="input-field" placeholder="you@example.com"
                                value={email} onChange={e => setEmail(e.target.value)} required
                                style={{ paddingLeft: 42 }} />
                        </div>
                    </div>

                    <div className="input-group">
                        <label htmlFor="login-password">Password</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input id="login-password" type="password" className="input-field" placeholder="••••••••"
                                value={password} onChange={e => setPassword(e.target.value)} required
                                style={{ paddingLeft: 42 }} />
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading}
                        style={{ width: '100%', padding: '14px 24px', marginTop: 8 }}>
                        {loading ? <span className="spinner" /> : <><span>Sign In</span><ArrowRight size={18} /></>}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: 24, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    Don't have an account?{' '}
                    <Link to="/register" style={{ color: 'var(--accent-secondary)', textDecoration: 'none', fontWeight: 600 }}>
                        Create one
                    </Link>
                </p>
            </motion.div>
        </div>
    );
}

export function RegisterPage() {
    const [form, setForm] = useState({ email: '', password: '', full_name: '', phone: '' });
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await register(form.email, form.password, form.full_name, form.phone || undefined);
            toast.success('Account created!');
            navigate('/dashboard');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    const update = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }));

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="glass-card"
                style={{ width: '100%', maxWidth: 440, padding: 40 }}
            >
                <div style={{ textAlign: 'center', marginBottom: 32 }}>
                    <div style={{
                        width: 56, height: 56, borderRadius: 16,
                        background: 'var(--accent-gradient)',
                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                        marginBottom: 16, boxShadow: '0 0 40px rgba(108, 92, 231, 0.3)',
                    }}>
                        <Plane size={28} color="white" />
                    </div>
                    <h1 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: 8 }}>Create Account</h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Start planning AI-powered trips</p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div className="input-group">
                        <label htmlFor="reg-name">Full Name</label>
                        <div style={{ position: 'relative' }}>
                            <User size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input id="reg-name" className="input-field" placeholder="Your Name"
                                value={form.full_name} onChange={update('full_name')} required style={{ paddingLeft: 42 }} />
                        </div>
                    </div>
                    <div className="input-group">
                        <label htmlFor="reg-email">Email</label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input id="reg-email" type="email" className="input-field" placeholder="you@example.com"
                                value={form.email} onChange={update('email')} required style={{ paddingLeft: 42 }} />
                        </div>
                    </div>
                    <div className="input-group">
                        <label htmlFor="reg-phone">Phone (optional)</label>
                        <div style={{ position: 'relative' }}>
                            <Phone size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input id="reg-phone" className="input-field" placeholder="+91 98765 43210"
                                value={form.phone} onChange={update('phone')} style={{ paddingLeft: 42 }} />
                        </div>
                    </div>
                    <div className="input-group">
                        <label htmlFor="reg-password">Password</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input id="reg-password" type="password" className="input-field" placeholder="••••••••"
                                value={form.password} onChange={update('password')} required minLength={6} style={{ paddingLeft: 42 }} />
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading}
                        style={{ width: '100%', padding: '14px 24px', marginTop: 8 }}>
                        {loading ? <span className="spinner" /> : <><span>Create Account</span><ArrowRight size={18} /></>}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: 24, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    Already have an account?{' '}
                    <Link to="/login" style={{ color: 'var(--accent-secondary)', textDecoration: 'none', fontWeight: 600 }}>Sign in</Link>
                </p>
            </motion.div>
        </div>
    );
}
