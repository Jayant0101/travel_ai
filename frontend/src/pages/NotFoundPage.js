import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import './NotFoundPage.css';

export default function NotFoundPage() {
    return (
        <section className="notfound-page">
            <h1 className="notfound-title">404</h1>
            <p className="notfound-message">Oops! The page you’re looking for doesn’t exist.</p>
            <Link to="/" className="btn btn-primary notfound-home-link">
                <ArrowLeft size={18} />
                Back to Home
            </Link>
        </section>
    );
}
