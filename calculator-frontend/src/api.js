import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

export const calculateExpression = async (data) => {
    return await axios.post(`${API_URL}/calculate`, data);
};

export const fetchHistory = async () => {
    return await axios.get(`${API_URL}/export-csv`);
};
