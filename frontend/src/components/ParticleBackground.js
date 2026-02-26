import React, { useRef, useEffect } from 'react';

/**
 * Animated particle canvas background — inspired by Spaceship.com
 * Creates floating stars/particles that react subtly to mouse movement
 */
export default function ParticleBackground() {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let animId;
        let mouse = { x: -1000, y: -1000 };

        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        resize();
        window.addEventListener('resize', resize);

        const handleMouse = (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        };
        window.addEventListener('mousemove', handleMouse);

        // Create particles
        const PARTICLE_COUNT = Math.min(120, Math.floor(window.innerWidth / 12));
        const particles = [];

        const colors = [
            'rgba(124, 58, 237, ',   // violet
            'rgba(168, 85, 247, ',   // purple
            'rgba(217, 70, 239, ',   // fuchsia
            'rgba(6, 182, 212, ',    // cyan
            'rgba(56, 189, 248, ',   // sky
            'rgba(20, 184, 166, ',   // teal
        ];

        for (let i = 0; i < PARTICLE_COUNT; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                radius: Math.random() * 2 + 0.5,
                color: colors[Math.floor(Math.random() * colors.length)],
                opacity: Math.random() * 0.5 + 0.1,
                pulseSpeed: Math.random() * 0.02 + 0.005,
                pulsePhase: Math.random() * Math.PI * 2,
            });
        }

        const CONNECTION_DISTANCE = 120;

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];

                // Subtle mouse repulsion
                const dx = p.x - mouse.x;
                const dy = p.y - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 200) {
                    const force = (200 - dist) / 200 * 0.02;
                    p.vx += dx * force * 0.01;
                    p.vy += dy * force * 0.01;
                }

                // Move
                p.x += p.vx;
                p.y += p.vy;

                // Dampen velocity
                p.vx *= 0.999;
                p.vy *= 0.999;

                // Wrap around edges
                if (p.x < -10) p.x = canvas.width + 10;
                if (p.x > canvas.width + 10) p.x = -10;
                if (p.y < -10) p.y = canvas.height + 10;
                if (p.y > canvas.height + 10) p.y = -10;

                // Pulse opacity
                p.pulsePhase += p.pulseSpeed;
                const currentOpacity = p.opacity * (0.6 + 0.4 * Math.sin(p.pulsePhase));

                // Draw particle
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color + currentOpacity + ')';
                ctx.fill();

                // Draw connections between nearby particles
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const cdx = p.x - p2.x;
                    const cdy = p.y - p2.y;
                    const cdist = Math.sqrt(cdx * cdx + cdy * cdy);

                    if (cdist < CONNECTION_DISTANCE) {
                        const lineOpacity = (1 - cdist / CONNECTION_DISTANCE) * 0.12;
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = `rgba(124, 58, 237, ${lineOpacity})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }

            animId = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            cancelAnimationFrame(animId);
            window.removeEventListener('resize', resize);
            window.removeEventListener('mousemove', handleMouse);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="particles-canvas"
            style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0, pointerEvents: 'none' }}
        />
    );
}
