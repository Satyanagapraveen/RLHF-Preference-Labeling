import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getNextPair = async (annotatorId) => {
    try {
        const response = await api.get(`/api/pairs/next?annotator_id=${annotatorId}`);
        return response.data;
    } catch (error) {
        if (error.response && error.response.status === 404) {
            return null; 
        }
        throw error;
    }
};

export const submitLabel = async (pairId, annotatorId, chosen) => {
    const response = await api.post('/api/labels', {
        pair_id: pairId,
        annotator_id: annotatorId,
        chosen: chosen,
    });
    return response.data;
};

export const getAnalytics = async () => {
    const response = await api.get('/api/analytics');
    return response.data;
};