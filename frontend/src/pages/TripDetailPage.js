import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    MapPin, Calendar, IndianRupee, Users, ArrowLeft, CheckCircle,
    Sun, Utensils, Hotel, Plane as PlaneIcon, Car, Lightbulb, CloudSun, Backpack
} from 'lucide-react';
import api from '../lib/api';
import toast from 'react-hot-toast';

export default function TripDetailPage() {
    const { tripId } = useParams();
    const [trip, setTrip] = useState(null);
    const [loading, setLoading] = useState(true);
    const [confirming, setConfirming] = useState(false);

    useEffect(() => {
        const fetch = async () => {
            try {
                const { data } = await api.get(`/trips/${tripId}`);
                setTrip(data);
            } catch (err) {
                toast.error('Failed to load trip details');
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, [tripId]);

    const confirmTrip = async () => {
        setConfirming(true);
        try {
            await api.put(`/trips/${tripId}/confirm`);
            setTrip(t => ({ ...t, status: 'confirmed' }));
            toast.success('Trip confirmed!');
        } catch (err) {
            toast.error('Failed to confirm trip');
        } finally {
            setConfirming(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-overlay" style={{ minHeight: '60vh' }}>
                <div className="spinner" style={{ width: 40, height: 40 }} />
                <p>Loading itinerary...</p>
            </div>
        );
    }

    if (!trip) {
        return (
            <div className="container" style={{ paddingTop: 60, textAlign: 'center' }}>
                <h2>Trip not found</h2>
                <Link to="/dashboard" className="btn btn-secondary" style={{ marginTop: 16 }}>Back to Dashboard</Link>
            </div>
        );
    }

    const itinerary = trip.itinerary;

    return (
        <div className="container" style={{ paddingTop: 32, paddingBottom: 60 }}>
            {/* Back button */}
            <Link to="/dashboard" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', textDecoration: 'none', marginBottom: 24, fontSize: '0.9rem' }}>
                <ArrowLeft size={16} /> Back to Dashboard
            </Link>

            {/* Trip header */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: 32, marginBottom: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
                    <div>
                        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: 8, background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                            {trip.destination}
                        </h1>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, color: 'var(--text-secondary)' }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><Calendar size={16} />{trip.start_date} → {trip.end_date}</span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><IndianRupee size={16} />₹{trip.budget?.toLocaleString()}</span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><Users size={16} />{trip.travelers} travelers</span>
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <span className={`badge ${trip.status === 'confirmed' ? 'badge-success' : 'badge-draft'}`}>{trip.status}</span>
                        {trip.status === 'draft' && (
                            <button onClick={confirmTrip} className="btn btn-primary" disabled={confirming} style={{ padding: '10px 20px' }}>
                                {confirming ? <span className="spinner" /> : <><CheckCircle size={16} /> Confirm Trip</>}
                            </button>
                        )}
                    </div>
                </div>

                {/* Estimated cost */}
                {itinerary?.estimated_cost && (
                    <div style={{ marginTop: 20, padding: '12px 20px', background: 'rgba(0, 206, 201, 0.08)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(0, 206, 201, 0.15)' }}>
                        <span style={{ color: 'var(--success)', fontWeight: 600 }}>Estimated Cost: ₹{itinerary.estimated_cost.toLocaleString()}</span>
                    </div>
                )}
            </motion.div>

            {itinerary && (
                <>
                    {/* Daily Plans */}
                    <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Sun size={22} style={{ color: 'var(--warning)' }} /> Day-by-Day Itinerary
                    </h2>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 32 }}>
                        {itinerary.daily_plans?.map((day, i) => (
                            <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                                className="glass-card" style={{ padding: 24 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                                    <h3 style={{ fontWeight: 700, fontSize: '1.1rem' }}>Day {day.day} — {day.title}</h3>
                                    <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{day.date}</span>
                                </div>
                                <p style={{ color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.7 }}>{day.description}</p>

                                {/* Activities */}
                                <div style={{ marginBottom: 16 }}>
                                    <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-secondary)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Activities</h4>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                        {day.activities?.map((a, j) => (
                                            <span key={j} style={{ padding: '6px 14px', background: 'rgba(108, 92, 231, 0.1)', borderRadius: 100, fontSize: '0.82rem', color: 'var(--accent-secondary)', border: '1px solid rgba(108, 92, 231, 0.15)' }}>
                                                {a}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {/* Meals */}
                                {day.meals?.length > 0 && (
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 8 }}>
                                        {day.meals.map((meal, j) => (
                                            <div key={j} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
                                                <Utensils size={14} style={{ color: 'var(--warning)', flexShrink: 0 }} />
                                                <div>
                                                    <div style={{ fontWeight: 500, textTransform: 'capitalize' }}>{meal.type}</div>
                                                    <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{meal.suggestion} • {meal.cost}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Accommodation */}
                                {day.accommodation && (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12, padding: '8px 12px', background: 'rgba(116, 185, 255, 0.06)', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
                                        <Hotel size={14} style={{ color: 'var(--info)', flexShrink: 0 }} />
                                        <span>{day.accommodation.name} — {day.accommodation.cost}</span>
                                    </div>
                                )}
                            </motion.div>
                        ))}
                    </div>

                    {/* Hotels, Flights, Transport, Tips in a grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 20, marginBottom: 32 }}>
                        {/* Hotels */}
                        {itinerary.hotels?.length > 0 && (
                            <div className="glass-card" style={{ padding: 24 }}>
                                <h3 style={{ fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Hotel size={18} style={{ color: 'var(--info)' }} /> Recommended Hotels
                                </h3>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    {itinerary.hotels.map((h, i) => (
                                        <div key={i} style={{ padding: '12px 16px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)' }}>
                                            <div style={{ fontWeight: 600, marginBottom: 4 }}>{h.name} <span style={{ color: 'var(--warning)', fontSize: '0.8rem' }}>★ {h.rating}</span></div>
                                            <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>₹{h.price_per_night?.toLocaleString()}/night • {h.location}</div>
                                            {h.amenities && <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 4 }}>{h.amenities.join(' • ')}</div>}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Flights */}
                        {itinerary.flights?.length > 0 && (
                            <div className="glass-card" style={{ padding: 24 }}>
                                <h3 style={{ fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <PlaneIcon size={18} style={{ color: 'var(--accent-secondary)' }} /> Flights
                                </h3>
                                {itinerary.flights.map((f, i) => (
                                    <div key={i} style={{ padding: '12px 16px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)', marginBottom: 8 }}>
                                        <div style={{ fontWeight: 600, marginBottom: 4 }}>{f.airline}</div>
                                        <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>{f.route} • ₹{f.price?.toLocaleString()} • {f.duration}</div>
                                        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{f.departure} → {f.arrival}</div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Local Transport */}
                        {itinerary.local_transport?.length > 0 && (
                            <div className="glass-card" style={{ padding: 24 }}>
                                <h3 style={{ fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Car size={18} style={{ color: 'var(--success)' }} /> Local Transport
                                </h3>
                                {itinerary.local_transport.map((t, i) => (
                                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 16px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)', marginBottom: 8, fontSize: '0.85rem' }}>
                                        <span><strong>{t.type}</strong> — {t.description}</span>
                                        <span style={{ color: 'var(--success)' }}>₹{t.cost?.toLocaleString()}</span>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Tips */}
                        {itinerary.tips?.length > 0 && (
                            <div className="glass-card" style={{ padding: 24 }}>
                                <h3 style={{ fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Lightbulb size={18} style={{ color: 'var(--warning)' }} /> Travel Tips
                                </h3>
                                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    {itinerary.tips.map((tip, i) => (
                                        <li key={i} style={{ padding: '8px 12px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                            💡 {tip}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Weather & Packing */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                        {itinerary.weather_info && (
                            <div className="glass-card" style={{ padding: 24 }}>
                                <h3 style={{ fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <CloudSun size={18} style={{ color: 'var(--info)' }} /> Weather
                                </h3>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.7 }}>{itinerary.weather_info}</p>
                            </div>
                        )}
                        {itinerary.packing_list?.length > 0 && (
                            <div className="glass-card" style={{ padding: 24 }}>
                                <h3 style={{ fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Backpack size={18} style={{ color: 'var(--accent-secondary)' }} /> Packing List
                                </h3>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                    {itinerary.packing_list.map((item, i) => (
                                        <span key={i} style={{ padding: '5px 12px', background: 'var(--bg-glass)', borderRadius: 100, fontSize: '0.8rem', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}>
                                            {item}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
