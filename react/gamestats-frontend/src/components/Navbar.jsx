import React from 'react';
import {Link} from 'react-router-dom';

const Navbar = () => {
    return (
        <nav className="bg-gray-800 text-white shadow-lg">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    <Link to="/" className="text-xl font-bold">
                        Game Stats Dashboard
                    </Link>
                    <div className="flex space-x-4">
                        <Link to = "/" className="px-3 py-2 rounded-md hover:bg-gray-700 transition">
                            대시보드
                        </Link>
                        <Link to = "/ranking" className="px-3 py-2 rounded-md hover:bg-gray-700 transition">
                            랭킹
                        </Link>
                        <Link to = "/items" className="px-3 py-2 rounded-md hover:bg-gray-700 transition">
                            아이템 분석
                        </Link>
                        <Link to = "/skills" className="px-3 py-2 rounded-md hover:bg-gray-700 transition">
                            스킬 분석
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;