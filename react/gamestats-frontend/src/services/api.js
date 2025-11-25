import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
    baseURL : API_BASE_URL,
    headers:{
        'Content-Type' : 'application/json',
    },
});

// 유저 관련 API
export const getUsers = (page = 1) => api.get(`/users/?page=${page}`);
export const getUserDetail = (id) => api.get(`/users/${id}/`);
export const getTopRankers = (limit = 100, tier = 'ALL') =>{
    let url = `/users/top_rankers/?limit=${limit}`;
    if(tier && tier !== 'ALL'){
        url += `&tier=${tier}`;
    }
    return api.get(url);
};
export const getTierStats = () => api.get('/users/tier_stats/');

// 아이템 관련 API
export const getItems = () => api.get('/items/');
export const getPopularItems = (params = {}) => {

    const { type, tier, limit = 10 } = params;
    let url = `/items/popular_items/?limit=${limit}`;
    if (type) url += `&type=${type}`;
    if (tier) url += `&tier=${tier}`;
    return api.get(url);

};

// 스킬 관련 API
export const getSkills = () => api.get('/skills/');
export const getPopularSkills = (params = {}) => {

    const {type, tier, limit = 10} = params;
    let url = `/skills/popular_skills/?limit=${limit}`;
    if (type) url += `&type=${type}`;
    if (tier) url += `&tier=${tier}`;
    return api.get(url);

};

// 통계 관련 API
export const getTopPlayerItems = (topPercent = 10) =>
    api.get(`/stats/top_players_items/?top_percent=${topPercent}`);
export const getTopPlayerSkills = (topPercent = 10) =>
    api.get(`/stats/top_players_skills/?top_percent=${topPercent}`);

export default api;