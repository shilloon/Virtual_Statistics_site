import React, {useEffect, useState} from 'react';
import { getTopRankers } from '../services/api';

const RankingTable = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [limit, setLimit] = useState(100);
    const [selectedTier, setSelectedTier] = useState('ALL');

    const tiers = ['ALL', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER'];

    useEffect(() => {
        const fetchRankers = async () => {
            setLoading(true);
            try{
                const response = await getTopRankers(limit);
                setUsers(response.data);
                setLoading(false);
            }
            catch(error){
                console.error('랭킹 데이터 로딩 실패:', error);
                setLoading(false);
            }
        };
        fetchRankers();
    }, [limit]);

    // 티어 필터링
    const filteredUsers = selectedTier === 'ALL' ? users : users.filter(user => user.tier === selectedTier);

    if(loading){
        return(
            <div className='flex justify-center items-center h-64'>
                <div className="text-xl">로딩 중...</div>
            </div>
        );
    }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">유저 랭킹</h1>

      {/* 필터 */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium mb-2">표시 개수</label>
            <select 
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="px-4 py-2 border rounded-lg"
            >
              <option value={50}>50명</option>
              <option value={100}>100명</option>
              <option value={200}>200명</option>
              <option value={500}>500명</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">티어 필터</label>
            <select 
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              {tiers.map(tier => (
                <option key={tier} value={tier}>{tier}</option>
              ))}
            </select>
          </div>

          <div className="ml-auto">
            <p className="text-sm text-gray-600">
              총 {filteredUsers.length}명의 유저
            </p>
          </div>
        </div>
      </div>

      {/* 랭킹 테이블 */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 text-white">
              <tr>
                <th className="px-4 py-3 text-left">순위</th>
                <th className="px-4 py-3 text-left">닉네임</th>
                <th className="px-4 py-3 text-left">티어</th>
                <th className="px-4 py-3 text-left">레벨</th>
                <th className="px-4 py-3 text-left">랭킹 점수</th>
                <th className="px-4 py-3 text-left">승률</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user, index) => (
                <tr 
                  key={user.id} 
                  className={`border-b hover:bg-gray-50 ${
                    index < 3 ? 'bg-yellow-50' : ''
                  }`}
                >
                  <td className="px-4 py-3">
                    {index === 0}
                    {index === 1}
                    {index === 2}
                    {index > 2 && index + 1}
                  </td>
                  <td className="px-4 py-3 font-semibold">{user.nickname}</td>
                  <td className="px-4 py-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      user.tier === 'GRANDMASTER' ? 'bg-red-100 text-red-800' :
                      user.tier === 'MASTER' ? 'bg-purple-100 text-purple-800' :
                      user.tier === 'DIAMOND' ? 'bg-blue-100 text-blue-800' :
                      user.tier === 'PLATINUM' ? 'bg-cyan-100 text-cyan-800' :
                      user.tier === 'GOLD' ? 'bg-yellow-100 text-yellow-800' :
                      user.tier === 'SILVER' ? 'bg-gray-100 text-gray-800' :
                      'bg-orange-100 text-orange-800'
                    }`}>
                      {user.tier}
                    </span>
                  </td>
                  <td className="px-4 py-3">{user.level}</td>
                  <td className="px-4 py-3 font-bold text-blue-600">
                    {user.ranking_score.toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`${
                      user.win_rate >= 60 ? 'text-green-600' :
                      user.win_rate >= 50 ? 'text-blue-600' :
                      'text-red-600'
                    }`}>
                      {user.win_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RankingTable;