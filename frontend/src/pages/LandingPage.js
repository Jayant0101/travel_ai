import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, MapPin, Shield, Zap, Globe, ArrowRight, Plane, Star, Clock, CreditCard, Users, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const fadeUp = (delay = 0) => ({
    initial: { opacity: 0, y: 40 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.7, delay, ease: [0.25, 0.46, 0.45, 0.94] },
});

const features = [
    { icon: Sparkles, title: 'AI-Powered Itineraries', desc: 'Gemini AI crafts personalized day-by-day plans with restaurants, hotels, and hidden gems', color: '#a855f7' },
    { icon: Shield, title: 'Enterprise Reliability', desc: 'Circuit breakers, caching, and auto-scaling handle 100K+ concurrent travelers', color: '#06b6d4' },
    { icon: Zap, title: 'Instant Generation', desc: 'Smart caching delivers popular destinations instantly. Unique plans in under 60 seconds', color: '#f59e0b' },
    { icon: Globe, title: 'Worldwide Coverage', desc: 'From Goa to Paris, Manali to Tokyo — complete itineraries for 500+ destinations', color: '#10b981' },
    { icon: CreditCard, title: 'Integrated Booking', desc: 'Book flights, hotels, and local transport directly from your AI-generated plan', color: '#f43f5e' },
    { icon: Users, title: 'Group Planning', desc: 'Plan for solo trips, couples, families, or large groups with budget optimization', color: '#3b82f6' },
];

const stats = [
    { value: '500+', label: 'Destinations' },
    { value: '50K+', label: 'Trips Generated' },
    { value: '98%', label: 'Satisfaction Rate' },
    { value: '< 60s', label: 'Generation Time' },
];

const destinations = [
    { name: 'Goa', tag: 'Beach & Nightlife', gradient: 'linear-gradient(135deg, #f43f5e, #f59e0b)' },
    { name: 'Manali', tag: 'Mountains & Snow', gradient: 'linear-gradient(135deg, #3b82f6, #06b6d4)' },
    { name: 'Jaipur', tag: 'Culture & Heritage', gradient: 'linear-gradient(135deg, #f59e0b, #f43f5e)' },
    { name: 'Kerala', tag: 'Nature & Wellness', gradient: 'linear-gradient(135deg, #10b981, #14b8a6)' },
    { name: 'Paris', tag: 'Romance & Art', gradient: 'linear-gradient(135deg, #a855f7, #d946ef)' },
    { name: 'Tokyo', tag: 'Tech & Tradition', gradient: 'linear-gradient(135deg, #7c3aed, #3b82f6)' },
];

export default function LandingPage() {
    const { user } = useAuth();

    return (
        <div style={{ position: 'relative', zIndex: 1 }}>

            {/* ═══ HERO SECTION ═══ */}
            <section style={{ padding: '120px 24px 100px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>

                <motion.div {...fadeUp(0)}>
                    <div style={{
                        display: 'inline-flex', padding: '6px 20px', borderRadius: 100,
                        background: 'rgba(124, 58, 237, 0.1)', border: '1px solid rgba(124, 58, 237, 0.25)',
                        color: '#a855f7', fontSize: '0.8rem', fontWeight: 600,
                        marginBottom: 28, gap: 8, alignItems: 'center',
                        animation: 'float 4s ease-in-out infinite',
                    }}>
                        <Sparkles size={14} /> AI-Powered Travel Planning
                    </div>
                </motion.div>

                <motion.h1 {...fadeUp(0.15)} style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: 'clamp(2.8rem, 6vw, 5rem)',
                    fontWeight: 900,
                    lineHeight: 1.05,
                    letterSpacing: '-0.04em',
                    maxWidth: 800,
                    margin: '0 auto 24px',
                }}>
                    Your Dream Trip,{' '}
                    <span style={{
                        background: 'var(--gradient-hero)',
                        backgroundSize: '200% auto',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        animation: 'textGradient 4s linear infinite',
                    }}>
                        Planned in Seconds
                    </span>
                </motion.h1>

                <motion.p {...fadeUp(0.3)} style={{
                    fontSize: '1.2rem', color: 'var(--text-secondary)',
                    maxWidth: 560, margin: '0 auto 48px', lineHeight: 1.7,
                }}>
                    Tell us your destination and budget. Our AI creates complete day-by-day itineraries with hotels, flights, restaurants, and activities — like a personal travel agent that never sleeps.
                </motion.p>

                <motion.div {...fadeUp(0.45)} style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
                    <Link to={user ? '/generate' : '/register'} className="btn btn-primary" style={{ padding: '18px 40px', fontSize: '1.1rem', borderRadius: 'var(--radius-xl)' }}>
                        {user ? 'Plan a Trip' : 'Start Free'} <ArrowRight size={20} />
                    </Link>
                    {!user && (
                        <Link to="/login" className="btn btn-secondary" style={{ padding: '18px 40px', fontSize: '1.1rem', borderRadius: 'var(--radius-xl)' }}>
                            Sign In
                        </Link>
                    )}
                </motion.div>

                {/* Hero decorative elements */}
                <motion.div {...fadeUp(0.6)} style={{ marginTop: 60, display: 'flex', justifyContent: 'center', gap: 8, flexWrap: 'wrap' }}>
                    {['Goa', 'Manali', 'Paris', 'Tokyo', 'Bali', 'Dubai'].map((place, i) => (
                        <span key={i} style={{
                            padding: '6px 16px', borderRadius: 100,
                            background: 'rgba(255,255,255,0.03)',
                            border: '1px solid rgba(255,255,255,0.06)',
                            fontSize: '0.82rem', color: 'var(--text-muted)',
                        }}>
                            <MapPin size={12} style={{ display: 'inline', marginRight: 4 }} />{place}
                        </span>
                    ))}
                </motion.div>
            </section>

            {/* ═══ STATS BAR ═══ */}
            <section className="container" style={{ marginBottom: 80 }}>
                <motion.div {...fadeUp(0.2)} style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: 1,
                    background: 'var(--border)',
                    borderRadius: 'var(--radius-xl)',
                    overflow: 'hidden',
                }}>
                    {stats.map((s, i) => (
                        <div key={i} style={{
                            background: 'var(--bg-card)',
                            padding: '32px 24px',
                            textAlign: 'center',
                        }}>
                            <div className="stat-number">{s.value}</div>
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4, fontWeight: 500 }}>{s.label}</div>
                        </div>
                    ))}
                </motion.div>
            </section>

            {/* ═══ FEATURES ═══ */}
            <section className="container" style={{ marginBottom: 100 }}>
                <motion.div {...fadeUp(0)} style={{ textAlign: 'center', marginBottom: 56 }}>
                    <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
                        Everything You Need to{' '}
                        <span style={{ color: 'var(--purple)' }}>Travel Smart</span>
                    </h2>
                    <p style={{ color: 'var(--text-secondary)', marginTop: 12, fontSize: '1.05rem' }}>
                        A complete travel planning platform powered by artificial intelligence
                    </p>
                </motion.div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
                    {features.map((f, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 + i * 0.1, duration: 0.6 }}
                            className="glass-card"
                            style={{ padding: 32 }}
                        >
                            <div style={{
                                width: 52, height: 52, borderRadius: 16,
                                background: `${f.color}12`,
                                border: `1px solid ${f.color}28`,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                marginBottom: 20,
                            }}>
                                <f.icon size={26} style={{ color: f.color }} />
                            </div>
                            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', fontWeight: 700, marginBottom: 10 }}>{f.title}</h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.7 }}>{f.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* ═══ POPULAR DESTINATIONS ═══ */}
            <section className="container" style={{ marginBottom: 100 }}>
                <motion.div {...fadeUp(0)} style={{ textAlign: 'center', marginBottom: 48 }}>
                    <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
                        Popular <span style={{ color: 'var(--cyan)' }}>Destinations</span>
                    </h2>
                    <p style={{ color: 'var(--text-secondary)', marginTop: 10 }}>Click any destination to generate an instant AI itinerary</p>
                </motion.div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
                    {destinations.map((d, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.1 + i * 0.08 }}
                        >
                            <Link to={user ? '/generate' : '/register'}>
                                <div className="glass-card" style={{ padding: 24, textAlign: 'center', cursor: 'pointer' }}>
                                    <div style={{
                                        width: 56, height: 56, borderRadius: '50%',
                                        background: d.gradient,
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        margin: '0 auto 16px',
                                        boxShadow: `0 8px 30px ${d.gradient.includes('#f43f5e') ? 'rgba(244,63,94,0.2)' : 'rgba(124,58,237,0.2)'}`,
                                    }}>
                                        <Plane size={24} color="white" />
                                    </div>
                                    <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem', marginBottom: 4 }}>{d.name}</h3>
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>{d.tag}</p>
                                </div>
                            </Link>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* ═══ HOW IT WORKS ═══ */}
            <section className="container" style={{ marginBottom: 100 }}>
                <motion.div {...fadeUp(0)} style={{ textAlign: 'center', marginBottom: 56 }}>
                    <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', fontWeight: 800 }}>
                        Three Steps to Your <span style={{ color: 'var(--emerald)' }}>Perfect Trip</span>
                    </h2>
                </motion.div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 32 }}>
                    {[
                        { step: '01', icon: MapPin, title: 'Choose Destination', desc: 'Enter where you want to go, your travel dates, budget, and preferences. Our AI handles the rest.', color: '#a855f7' },
                        { step: '02', icon: Sparkles, title: 'AI Creates Your Plan', desc: 'Gemini AI generates a complete itinerary with hotels, flights, daily activities, meals, and tips.', color: '#06b6d4' },
                        { step: '03', icon: CheckCircle, title: 'Confirm & Travel', desc: 'Review the plan, make adjustments, confirm your trip, and book everything in one click.', color: '#10b981' },
                    ].map((s, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 + i * 0.15 }}
                            style={{ textAlign: 'center', padding: '40px 24px', position: 'relative' }}
                        >
                            <div style={{
                                width: 72, height: 72, borderRadius: 24,
                                background: `${s.color}10`,
                                border: `1px solid ${s.color}25`,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                margin: '0 auto 20px',
                                position: 'relative',
                            }}>
                                <s.icon size={32} style={{ color: s.color }} />
                                <span style={{
                                    position: 'absolute', top: -8, right: -8,
                                    width: 28, height: 28, borderRadius: '50%',
                                    background: s.color, color: 'white',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    fontSize: '0.7rem', fontWeight: 800,
                                }}>{s.step}</span>
                            </div>
                            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', fontWeight: 700, marginBottom: 12 }}>{s.title}</h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.7 }}>{s.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* ═══ CTA ═══ */}
            <section className="container" style={{ marginBottom: 80 }}>
                <motion.div
                    {...fadeUp(0)}
                    className="glass-card"
                    style={{
                        padding: '64px 40px',
                        textAlign: 'center',
                        background: 'linear-gradient(135deg, rgba(124,58,237,0.1), rgba(6,182,212,0.08))',
                        borderColor: 'rgba(124,58,237,0.2)',
                    }}
                >
                    <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 800, marginBottom: 16 }}>
                        Ready to Plan Your Next Adventure?
                    </h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: 32, maxWidth: 500, margin: '0 auto 32px', fontSize: '1.05rem' }}>
                        Join thousands of travelers who plan smarter with AI. Free to start, no credit card required.
                    </p>
                    <Link to={user ? '/generate' : '/register'} className="btn btn-primary" style={{ padding: '18px 48px', fontSize: '1.1rem', borderRadius: 'var(--radius-xl)' }}>
                        <Sparkles size={20} /> {user ? 'Generate a Trip Now' : 'Get Started Free'}
                    </Link>
                </motion.div>
            </section>

            {/* ═══ FOOTER ═══ */}
            <footer style={{ borderTop: '1px solid var(--border)', padding: '32px 24px' }}>
                <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{ width: 32, height: 32, borderRadius: 10, background: 'var(--gradient-btn)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Plane size={16} color="white" />
                        </div>
                        <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1rem' }}>Travel AI</span>
                    </div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                        © 2026 Travel AI — Enterprise-grade AI travel planning
                    </p>
                </div>
            </footer>
        </div>
    );
}
