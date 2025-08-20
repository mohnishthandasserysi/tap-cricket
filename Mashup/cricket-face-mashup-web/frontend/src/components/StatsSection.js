import React from 'react';
import { Trophy, Target, Zap, Users } from 'lucide-react';

function StatsSection({ score, totalQuestions, stats, playersCount }) {
  const accuracy = totalQuestions > 0 ? Math.round((score / totalQuestions) * 100) : 0;
  
  // Function to determine accuracy color
  const getAccuracyColor = (acc) => {
    if (acc >= 80) return 'bg-green-500';
    if (acc >= 60) return 'bg-yellow-500';
    if (acc >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  // Function to determine accuracy text
  const getAccuracyText = (acc) => {
    if (acc >= 80) return 'Excellent!';
    if (acc >= 60) return 'Good!';
    if (acc >= 40) return 'Keep trying!';
    return 'Practice more!';
  };

  return (
    <div className="stats-section space-y-6">
      {/* Score Card */}
      <div className="card p-6 bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-800">Your Score</h3>
          </div>
          <div className="text-2xl font-bold text-blue-600">{score}</div>
        </div>
        
        {/* Accuracy Bar */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">Accuracy</span>
            <span className="font-medium text-gray-800">{accuracy}%</span>
          </div>
          <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`absolute left-0 top-0 h-full transition-all duration-500 rounded-full ${getAccuracyColor(accuracy)}`}
              style={{ width: `${accuracy}%` }}
            ></div>
          </div>
          <div className="text-sm text-center font-medium text-gray-600">
            {getAccuracyText(accuracy)}
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-white rounded-lg shadow-sm">
            <div className="text-sm text-gray-600">Questions</div>
            <div className="text-xl font-bold text-gray-800">{totalQuestions}</div>
          </div>
          <div className="text-center p-3 bg-white rounded-lg shadow-sm">
            <div className="text-sm text-gray-600">Success Rate</div>
            <div className="text-xl font-bold text-gray-800">{accuracy}%</div>
          </div>
        </div>
      </div>

      {/* Streaks */}
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Zap className="h-5 w-5 text-yellow-500" />
          <h3 className="text-lg font-semibold text-gray-800">Streaks</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
            <div className="text-sm text-gray-600">Current</div>
            <div className="text-xl font-bold text-purple-600">{stats.currentStreak}</div>
          </div>
          <div className="text-center p-3 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
            <div className="text-sm text-gray-600">Best</div>
            <div className="text-xl font-bold text-blue-600">{stats.bestStreak}</div>
          </div>
        </div>
      </div>

      {/* Available Players */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-green-500" />
            <h3 className="text-lg font-semibold text-gray-800">Players</h3>
          </div>
          <div className="text-xl font-bold text-green-600">{playersCount}</div>
        </div>
      </div>
    </div>
  );
}

export default StatsSection;