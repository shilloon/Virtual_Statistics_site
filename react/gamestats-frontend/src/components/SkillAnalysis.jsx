import React, { useEffect, useState } from 'react';
import { getPopularSkills, getTopPlayerSkills } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell} from 'recharts';

const SkillAnalysis = () => {
    const [popularSkills, setPopularSkills] = useState([]);
    const [topPlayerSkills, setTopPlayerSkills] = useState([]);
    const [loading, setLoading] = useState(true);
    const [skillType, setSkillType] = useState('ALL');
    const [tier, setTier] = useState('ALL');

    const skillTypes = ['ALL', 'ACTIVE', 'PASSIVE', 'ULTIMATE'];
    const tiers = ['ALL', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER'];

    useEffect(() => {
        const fetchData = async () =>{
            setLoading(true);
            try{
                const params = {limit:10};
                if (skillType !== 'ALL') params.type = skillType;
                if(tier !== 'ALL') params.tier = tier;

                const [popularRes, topPlayerRes] = await Promise.all([
                    getPopularSkills(params),
                    getTopPlayerSkills(10)
                ]);
                
                setPopularSkills(popularRes.data);
                setTopPlayerSkills(topPlayerRes.data.skills);
                setLoading(false);
            }
            catch (error) {
                console.error('스킬 데이터 로딩 실패:', error);
                setLoading(false);
            }
        };
        fetchData();
    }, [skillType, tier]);

    if(loading){
        return(
            <div className = "flex justify-center items-center h-64">
                <div className='text-xl'>로딩 중...</div>
            </div>
        );
    }

    // 차트 데이터 반환
    const chartData = popularSkills.map(skill => ({
        name: skill.name,
        사용횟수: skill.total_usage || 0,
    }));

    // 스킬 타입별 분포
    const typeDistribution = popularSkills.reduce((acc, skill) => {
        acc[skill.skill_type] = (acc[skill.skill_type] || 0) + 1;
        return acc;
    }, {});

    const pieData = Object.entries(typeDistribution).map(([type, count]) => ({
        name: type,
        value: count
    }));

    const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">스킬 분석</h1>

      {/* 필터 */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">스킬 타입</label>
            <select 
              value={skillType}
              onChange={(e) => setSkillType(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              {skillTypes.map(type => (
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

      {/* 스킬 타입 분포 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">인기 스킬 Top 10</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="사용횟수" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">스킬 타입 분포</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 인기 스킬 테이블 */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-bold mb-4">인기 스킬 상세</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">순위</th>
                <th className="px-4 py-2 text-left">스킬명</th>
                <th className="px-4 py-2 text-left">타입</th>
                <th className="px-4 py-2 text-left">설명</th>
                <th className="px-4 py-2 text-left">쿨다운</th>
              </tr>
            </thead>
            <tbody>
              {popularSkills.map((skill, index) => (
                <tr key={skill.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{index + 1}</td>
                  <td className="px-4 py-2 font-semibold">{skill.name}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      skill.skill_type === 'ACTIVE' ? 'bg-blue-100 text-blue-800' :
                      skill.skill_type === 'PASSIVE' ? 'bg-green-100 text-green-800' :
                      'bg-orange-100 text-orange-800'
                    }`}>
                      {skill.skill_type}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-600">{skill.description}</td>
                  <td className="px-4 py-2">
                    {skill.cooldown === 0 ? '-' : `${skill.cooldown}초`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 상위 랭커 선호 스킬 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">상위 10% 랭커 선호 스킬</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {topPlayerSkills.slice(0, 6).map((skill, index) => (
            <div key={skill.id} className="border rounded-lg p-4 hover:shadow-lg transition">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-bold text-lg">{skill.name}</h3>
                <span className="text-sm text-gray-500">#{index + 1}</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{skill.description}</p>
              <div className="flex justify-between items-center">
                <span className={`px-2 py-1 rounded text-xs ${
                  skill.skill_type === 'ACTIVE' ? 'bg-blue-100 text-blue-800' :
                  skill.skill_type === 'PASSIVE' ? 'bg-green-100 text-green-800' :
                  'bg-orange-100 text-orange-800'
                }`}>
                  {skill.skill_type}
                </span>
                <span className="text-sm font-semibold text-purple-600">
                  {skill.cooldown === 0 ? 'Passive' : `${skill.cooldown}초`}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

}

export default SkillAnalysis;