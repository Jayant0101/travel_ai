import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapPin, Calendar, IndianRupee, Users, Sparkles, Mountain, Baby, Leaf, Wallet, Crown } from 'lucide-react';
import api from '../lib/api';
import toast from 'react-hot-toast';

const preferenceOptions = [
    { key: 'adventure', label: 'Adventure', icon: Mountain, color: '#ff7675' },
    { key: 'family_friendly', label: 'Family', icon: Baby, color: '#74b9ff' },
    { key: 'vegetarian', label: 'Vegetarian', icon: Leaf, color: '#00cec9' },
    { key: 'budget_conscious', label: 'Budget', icon: Wallet, color: '#fdcb6e' },
    { key: 'luxury', label: 'Luxury', icon: Crown, color: '#a29bfe' },
];

export default function GeneratePage() {
    const [form, setForm] = useState({
        destination: '', start_date: '', end_date: '',
        budget: '', travelers: 1,
        preferences: { adventure: false, family_friendly: false, vegetarian: false, budget_conscious: false, luxury: false },
    });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const update = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }));
    const togglePref = (key) => setForm(f => ({
        ...f,
        preferences: { ...f.preferences, [key]: !f.preferences[key] }
    }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload = { ...form, budget: parseFloat(form.budget), travelers: parseInt(form.travelers) };
            const { data } = await api.post('/trips/generate', payload);
            toast.success('Itinerary generated!');
            navigate(`/trip/${data.id}`);
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to generate itinerary';
            if (err.response?.status === 429) {
                toast.error('Server is busy. Try again in a few seconds.');
            } else {
                toast.error(msg);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container" style={{ paddingTop: 40, paddingBottom: 60, maxWidth: 700 }}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <div className="page-header" style={{ textAlign: 'center' }}>
                    <h1>✨ Generate Your Trip</h1>
                    <p>Tell us where you want to go and our AI will plan the perfect itinerary</p>
                </div>

                <form onSubmit={handleSubmit} className="glass-card" style={{ padding: 32 }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                        {/* Destination */}
                        <div className="input-group">
                            <label htmlFor="gen-dest"><MapPin size={14} style={{ display: 'inline', marginRight: 6 }} />Destination</label>
                            <input id="gen-dest" className="input-field" placeholder="e.g. Goa, Manali, Paris..."
                                value={form.destination} onChange={update('destination')} required />
                        </div>

                        {/* Dates */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                            <div className="input-group">
                                <label htmlFor="gen-start"><Calendar size={14} style={{ display: 'inline', marginRight: 6 }} />Start Date</label>
                                <input id="gen-start" type="date" className="input-field"
                                    value={form.start_date} onChange={update('start_date')} required />
                            </div>
                            <div className="input-group">
                                <label htmlFor="gen-end">End Date</label>
                                <input id="gen-end" type="date" className="input-field"
                                    value={form.end_date} onChange={update('end_date')} required />
                            </div>
                        </div>

                        {/* Budget & Travelers */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                            <div className="input-group">
                                <label htmlFor="gen-budget"><IndianRupee size={14} style={{ display: 'inline', marginRight: 6 }} />Total Budget (₹)</label>
                                <input id="gen-budget" type="number" className="input-field" placeholder="50000"
                                    value={form.budget} onChange={update('budget')} required min="1000" />
                            </div>
                            <div className="input-group">
                                <label htmlFor="gen-travelers"><Users size={14} style={{ display: 'inline', marginRight: 6 }} />Travelers</label>
                                <input id="gen-travelers" type="number" className="input-field"
                                    value={form.travelers} onChange={update('travelers')} required min="1" max="20" />
                            </div>
                        </div>

                        {/* Preferences */}
                        <div>
                            <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 10, display: 'block' }}>
                                Preferences
                            </label>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                                {preferenceOptions.map(({ key, label, icon: Icon, color }) => (
                                    <button
                                        key={key}
                                        type="button"
                                        onClick={() => togglePref(key)}
                                        style={{
                                            display: 'flex', alignItems: 'center', gap: 8,
                                            padding: '10px 16px',
                                            background: form.preferences[key] ? `${color}20` : 'var(--bg-glass)',
                                            border: `1px solid ${form.preferences[key] ? `${color}50` : 'var(--border)'}`,
                                            borderRadius: 'var(--radius-md)',
                                            color: form.preferences[key] ? color : 'var(--text-secondary)',
                                            cursor: 'pointer',
                                            fontFamily: 'var(--font)',
                                            fontSize: '0.85rem',
                                            fontWeight: 500,
                                            transition: 'all 0.2s',
                                        }}
                                    >
                                        <Icon size={16} />
                                        {label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Submit */}
                        <button type="submit" className="btn btn-primary" disabled={loading}
                            style={{ width: '100%', padding: '16px 24px', fontSize: '1rem', marginTop: 8 }}>
                            {loading ? (
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                    <span className="spinner" />
                                    <span>AI is generating your itinerary...</span>
                                </div>
                            ) : (
                                <><Sparkles size={20} /> Generate AI Itinerary</>
                            )}
                        </button>

                        {loading && (
                            <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                This may take 30-60 seconds. Our AI is crafting a personalized plan for you.
                            </p>
                        )}
                    </div>
                </form>
            </motion.div>
        </div>
    );
}
