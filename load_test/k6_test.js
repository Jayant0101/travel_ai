// load_test/k6_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '2m', target: 1000 }, // ramp-up to 1k users
        { duration: '5m', target: 1000 }, // stay at 1k
        { duration: '2m', target: 5000 }, // ramp-up to 5k
        { duration: '5m', target: 5000 }, // stay at 5k
        { duration: '2m', target: 10000 }, // ramp-up to 10k
        { duration: '5m', target: 10000 }, // stay at 10k
        // For real 100k you would need distributed load generators
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests < 500ms
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api';

export default function () {
    // Simulate typical user flow: fetch trips, fetch a trip detail, confirm a trip
    const tripsRes = http.get(`${BASE_URL}/trips`);
    check(tripsRes, { 'GET /trips status 200': (r) => r.status === 200 });

    if (tripsRes.json().length > 0) {
        const tripId = tripsRes.json()[0].id;
        const detailRes = http.get(`${BASE_URL}/trips/${tripId}`);
        check(detailRes, { 'GET /trips/:id status 200': (r) => r.status === 200 });

        // Randomly confirm a draft trip
        if (detailRes.json().status === 'draft') {
            const confirmRes = http.put(`${BASE_URL}/trips/${tripId}/confirm`);
            check(confirmRes, { 'PUT /trips/:id/confirm 200': (r) => r.status === 200 });
        }
    }

    sleep(1);
}
