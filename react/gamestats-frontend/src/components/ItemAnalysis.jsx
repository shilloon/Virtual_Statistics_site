import React, {useEffect, useState} from 'react';
import { getPopularItems, getTopPlayerItems } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ItemAnalysis = () => {
    const [popularItems, setPopularItems] = useState([]);
    const [topPlayerItems, setTopPlayerItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [itemType, setItemType] = useState('ALL');
    const [tier, setTier] = useState('ALL');

    const itemTypes = ['ALL', 'WEAPON', 'ARMOR', 'ACCESSORY', 'CONSUMABLE'];
    const tiers = ['ALL', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER'];

    useEffect(() => {
        const fetchData = async() =>{
            setLoading(true);
            try{
                const params = {limit : 10};
                if(itemType !== 'ALL') params.type = itemType;
                if(tier !== 'ALL') params.tier = tier;

                const [popularRes, topPlayerRes] = await Promise.all([
                   getPopularItems(params),
                   getTopPlayerItems(10) 
                ]);

                setPopularItems(popularRes.data);
                setTopPlayerItems(topPlayerRes.data.items);
                setLoading(false);

            }
            catch(error){
                console.error('아이템 데이터 로딩 실패:', error);
                setLoading(false);
            }
        };
        fetchData();
    }, [itemType, tier]);

    if (loading){
        return (
            <div className='flex justify-center items-center h-64'>
                <div className="text-xl">로딩 중...</div>
            </div>
        );
    }

    // 차트 데이터 변환
    const chartData = popularItems.map(item => ({
        name: item.name,
        사용횟수: item.total_usage || 0,
    }));

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">아이템 분석</h1>

      {/* 필터 */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">아이템 타입</label>
            <select 
              value={itemType}
              onChange={(e) => setItemType(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              {itemTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">티어 필터</label>
            <select 
              value={tier}
              onChange={(e) => setTier(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              {tiers.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 인기 아이템 차트 */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-bold mb-4">인기 아이템 Top 10</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="사용횟수" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 인기 아이템 테이블 */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-bold mb-4">인기 아이템 상세</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">순위</th>
                <th className="px-4 py-2 text-left">아이템명</th>
                <th className="px-4 py-2 text-left">타입</th>
                <th className="px-4 py-2 text-left">설명</th>
                <th className="px-4 py-2 text-left">가격</th>
              </tr>
            </thead>
            <tbody>
              {popularItems.map((item, index) => (
                <tr key={item.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{index + 1}</td>
                  <td className="px-4 py-2 font-semibold">{item.name}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      item.item_type === 'WEAPON' ? 'bg-red-100 text-red-800' :
                      item.item_type === 'ARMOR' ? 'bg-blue-100 text-blue-800' :
                      item.item_type === 'ACCESSORY' ? 'bg-purple-100 text-purple-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {item.item_type}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-600">{item.description}</td>
                  <td className="px-4 py-2">{item.price.toLocaleString()} G</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 상위 랭커 선호 아이템 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">상위 10% 랭커 선호 아이템</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {topPlayerItems.slice(0, 6).map((item, index) => (
            <div key={item.id} className="border rounded-lg p-4 hover:shadow-lg transition">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-bold text-lg">{item.name}</h3>
                <span className="text-sm text-gray-500">#{index + 1}</span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{item.description}</p>
              <div className="flex justify-between items-center">
                <span className={`px-2 py-1 rounded text-xs ${
                  item.item_type === 'WEAPON' ? 'bg-red-100 text-red-800' :
                  item.item_type === 'ARMOR' ? 'bg-blue-100 text-blue-800' :
                  item.item_type === 'ACCESSORY' ? 'bg-purple-100 text-purple-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {item.item_type}
                </span>
                <span className="font-semibold text-blue-600">{item.price.toLocaleString()} G</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );  
};

export default ItemAnalysis;