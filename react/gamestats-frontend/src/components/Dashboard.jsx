import React, { useEffect, useState } from 'react';
import { getTierStats, getTopRankers } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const Dashboard = () => {
    const [tierStats, setTierStats] = useState(null);
    const [topRankers, setTopRankers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try{
                const [tierRes, rankerRes] = await Promise.all([
                    getTierStats(),
                    getTopRankers(10)
                ]);
                setTierStats(tierRes.data);
                setTopRankers(rankerRes.data);
                setLoading(false);
            }
            catch (error){
                console.error('데이터 로딩 실패:', error);
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if(loading){
        return(
            <div className='flex jusitfy-center items-center h-64'>
                <div className='text-xl'>로딩 중...</div>
            </div>
        );
    }

    // 티어별 데이터를 차트용으로 변환
    const chartData = tierStats ? Object.entries(tierStats).map(([tier, data]) => ({
        name:tier,
        value:data.count
    })) : [];

    const COLORS = ['#CD7F32', '#C0C0C0', '#FFD700', '#E5E4E2', '#B9F2FF', '#9370DB', '#FF6347'];

    // 전체 통계 계산
    const totalUsers = chartData.reduce((sum, item) => sum + item.value, 0);
    const avgLevel = tierStats ? Object.values(tierStats).reduce((sum, t) => sum + t.avg_level * t.count, 0) / totalUsers : 0;

    return(
        <div>
            <h1 className='text-3xl font-bold mb-8'>게임 통계 대시보드</h1>

            {/* 요약 카드 */}
            <div className='grid grid-cols-1 md:grid-cols-3 gap-6 mb-8'>
                <div className='bg-white p-6 rounded-lg shadow'>
                    <h3 className='text-gray-500 text-sm'>전체 유저</h3>
                    <p className='text-3xl font-bold text-blue-600'>{totalUsers.toLocaleString()}</p>
                </div>
                <div className='bg-white p-6 rounded-lg shadow'>
                    <h3 className='text-gray-500 text-sm'>평균 레벨</h3>
                    <p className='text-3xl font-bold text-green-600'>{avgLevel.toFixed(1)}</p>
                </div>
                <div className='bg-white p-6 rounded-lg shadow'>
                    <h3 className='text-gray-500 text-sm'>최고 티어 유저</h3>
                    <p className='text-3xl font-bold text-purple-600'>{tierStats?.GRANDMASTER?.count || 0}</p>
                </div>
            </div>

            {/* 티어 분포 차트 */}
            <div className='bg-white p-6 rounded-lg shadow mb-8'>
                <h2 className='text-xl font-bold mb-4'>티어별 유저 분포</h2>
                <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                        <Pie
                            data = {chartData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                            outerRadius={100}
                            fill="#8884d8"
                            datakey="value"
                        >
                            {chartData.map((entry, index) => (
                                <Cell key = {`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </div>
            
            {/* Top 10 랭커 */}
            <div className='bg-white p-6 rounded-lg shadow'>
                <h2 className="text-xl font-bold mb-4">Top 10 랭커</h2>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-2 text-left">순위</th>
                                <th className="px-4 py-2 text-left">닉네임</th>
                                <th className="px-4 py-2 text-left">티어</th>
                                <th className="px-4 py-2 text-left">레벨</th>
                                <th className="px-4 py-2 text-left">랭킹 점수</th>
                            </tr>
                        </thead>
                        <tbody>
                            {topRankers.map((user, index) => (
                                <tr key = {user.id} className='border-b horver:bg-gray-50'>
                                    <td className="px-4 py-2">{index + 1}</td>
                                    <td className="px-4 py-2 font-semibold">{user.nickname}</td>
                                    <td className="px-4 py-2">
                                        <span className = {`px-2 py-1 rounded text-sm ${
                                            user.tier === 'GRANDMASTER' ? 'bg-red-100 text-red-800' :
                                            user.tier === 'MASTER' ? 'bg-purple-100 text-purple-800':
                                            user.tier === 'DIAMOND' ? 'bj-blue-100 text-blue-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                            {user.tier}
                                        </span>
                                    </td>
                                    <td className="px-4 py-2">{user.level}</td>
                                    <td className="px-4 py-2">{user.ranking_score.toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;