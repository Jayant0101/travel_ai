import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapPin, Calendar, IndianRupee, Users, Plus, Sparkles, Clock } from 'lucide-react';
import api from '../lib/api';
import toast from 'react-hot-toast';

const statusBadge = (status) => {
    const map = {
        draft: 'badge-draft', confirmed: 'badge-success',
        completed: 'badge-info', cancelled: 'badge-warning',
    };
    return map[status] || 'badge-draft';
};

export default function DashboardPage() {
    const [trips, setTrips] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTrips = async () => {
            try {
                const { data } = await api.get('/trips');
                setTrips(data);
            } catch (err) {
                toast.error('Failed to load trips');
            } finally {
                setLoading(false);
            }
        };
        fetchTrips();
    }, []);

    if (loading) {
        return (
            <div className="loading-overlay">
                <div className="spinner" style={{ width: 40, height: 40 }} />
                <p>Loading your trips...</p>
            </div>
        );
    }

    return (
        <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 40, flexWrap: 'wrap', gap: 16 }}>
                <div className="page-header" style={{ marginBottom: 0 }}>
                    <h1>Your Trips</h1>
                    <p>{trips.length > 0 ? `${trips.length} trip${trips.length > 1 ? 's' : ''} planned` : 'No trips yet — create your first one!'}</p>
                </div>
                <Link to="/generate" className="btn btn-primary">
                    <Plus size={18} /> Generate New Trip
                </Link>
            </div>

            {/* Empty state */}
            {trips.length === 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card"
                    style={{ textAlign: 'center', padding: '80px 40px' }}
                >
                    <div style={{
                        width: 80, height: 80, borderRadius: 24,
                        background: 'var(--accent-gradient)',
                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                        marginBottom: 24, boxShadow: '0 0 60px rgba(108, 92, 231, 0.2)',
                    }}>
                        <Sparkles size={40} color="white" />
                    </div>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 12 }}>Plan Your First Trip</h2>
                    <p style={{ color: 'var(--text-secondary)', maxWidth: 400, margin: '0 auto 24px', lineHeight: 1.7 }}>
                        Our AI will generate a complete itinerary with hotels, flights, activities, and restaurants tailored to your preferences.
                    </p>
                    <Link to="/generate" className="btn btn-primary" style={{ padding: '14px 32px' }}>
                        <Sparkles size={18} /> Generate Itinerary
                    </Link>
                </motion.div>
            )}

            {/* Trip grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340, 1fr))', gap: 20 }}>
                {trips.map((trip, i) => (
                    <motion.div
                        key={trip.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.08 }}
                    >
                        <Link to={`/trip/${trip.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                            <div className="glass-card" style={{ padding: 24, cursor: 'pointer' }}>
                                {/* Destination header */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                        <div style={{
                                            width: 40, height: 40, borderRadius: 12,
                                            background: 'linear-gradient(135deg, rgba(108,92,231,0.2), rgba(116,185,255,0.2))',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        }}>
                                            <MapPin size={20} style={{ color: 'var(--accent-secondary)' }} />
                                        </div>
                                        <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>{trip.destination}</h3>
                                    </div>
                                    <span className={`badge ${statusBadge(trip.status)}`}>{trip.status}</span>
                                </div>

                                {/* Details */}
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        <Calendar size={14} />
                                        <span>{trip.start_date} → {trip.end_date}</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        <IndianRupee size={14} />
                                        <span>₹{trip.budget?.toLocaleString()}</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        <Users size={14} />
                                        <span>{trip.travelers} traveler{trip.travelers > 1 ? 's' : ''}</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        <Clock size={14} />
                                        <span>{new Date(trip.created_at).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            </div>
                        </Link>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
