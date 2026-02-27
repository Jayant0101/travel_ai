import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export default function NotFoundPage() {
    return (
        <section className="notfound-page" style={{ background: 'var(--bg-deep)', color: 'var(--text-primary)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <h1 className="notfound-title" style={{ fontSize: '6rem', marginBottom: '1rem' }}>404</h1>
            <p className="notfound-message" style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>Oops! The page you’re looking for doesn’t exist.</p>
            <Link to="/" className="btn btn-primary" style={{ background: 'var(--gradient-btn)', color: '#fff', padding: '0.75rem 1.5rem', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ArrowLeft size={18} />
                Back to Home
            </Link>
        </section>
    );
}
