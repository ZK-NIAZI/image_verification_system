import { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://vision.rentalforce.app';

export default function HealthBadge() {
    const [health, setHealth] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const res = await fetch(`${API_BASE}/health`);
                if (!res.ok) throw new Error('API error');
                const data = await res.json();
                setHealth(data);
            } catch {
                setHealth(null);
            } finally {
                setLoading(false);
            }
        };

        checkHealth();
        const interval = setInterval(checkHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    const getStatus = () => {
        if (loading) return { label: 'Checking...', dotClass: 'health-badge__dot--loading' };
        if (!health) return { label: 'API Offline', dotClass: 'health-badge__dot--offline' };
        if (health.status === 'healthy') return { label: `API Healthy · v${health.version}`, dotClass: 'health-badge__dot--healthy' };
        return { label: `Degraded · v${health.version}`, dotClass: 'health-badge__dot--degraded' };
    };

    const { label, dotClass } = getStatus();

    return (
        <div className="health-badge">
            <span className={`health-badge__dot ${dotClass}`} />
            {label}
        </div>
    );
}
