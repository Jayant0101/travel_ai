import React, { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';

/**
 * Simple theme toggle – switches between dark (default) and light mode.
 * Persists choice in localStorage and toggles a CSS class on the root element.
 */
export default function ThemeToggle() {
    const [isDark, setIsDark] = useState(() => {
        const saved = localStorage.getItem('theme');
        return saved ? saved === 'dark' : true; // default to dark
    });

    useEffect(() => {
        const root = document.documentElement;
        if (isDark) {
            root.classList.remove('light-theme');
        } else {
            root.classList.add('light-theme');
        }
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }, [isDark]);

    return (
        <button
            className="btn btn-ghost"
            onClick={() => setIsDark(!isDark)}
            title="Toggle dark / light mode"
            style={{ display: 'flex', alignItems: 'center', gap: 4 }}
        >
            {isDark ? <Moon size={18} /> : <Sun size={18} />}
        </button>
    );
}
