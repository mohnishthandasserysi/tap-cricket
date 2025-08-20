import React from 'react';
import { Trophy, Target, TrendingUp, Users, Star, Zap } from 'lucide-react';

const StatsSection = ({ score, totalQuestions, stats, playersCount }) => {
  const accuracy = totalQuestions > 0 ? Math.round((score / totalQuestions) * 100) : 0;
  
  return (
    <div className="space-y-6">
      {/* Score Card */}
      <div className="card p-6 bg-gradient-to-br from-green-50 to-blue-50 border-green-200">
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-2">
            <Trophy className="h-6 w-6 text-yellow-500" />
            <h3 className="text-xl font-bold text-gray-800">Your Score</h3>
          </div>
          
          <div className="space-y-2">
            <div className="text-4xl font-bold text-green-600">
              {score}/{totalQuestions}
            </div>
            <p className="text-gray-600">
              {totalQuestions === 0 ? 'No games played yet' : 'Correct answers'}
            </p>
          </div>
          
          {totalQuestions > 0 && (
            <div className="pt-2">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Target className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-700">Accuracy</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {accuracy}%
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card p-4 text-center">
          <div className="space-y-2">
            <div className="flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-green-500" />
            </div>
            <div className="text-lg font-bold text-gray-800">
              {stats.currentStreak || 0}
            </div>
            <p className="text-xs text-gray-600">Current Streak</p>
          </div>
        </div>
        
        <div className="card p-4 text-center">
          <div className="space-y-2">
            <div className="flex items-center justify-center">
              <Star className="h-5 w-5 text-yellow-500" />
            </div>
            <div className="text-lg font-bold text-gray-800">
              {stats.bestStreak || 0}
            </div>
            <p className="text-xs text-gray-600">Best Streak</p>
          </div>
        </div>
        
        <div className="card p-4 text-center">
          <div className="space-y-2">
            <div className="flex items-center justify-center">
              <Users className="h-5 w-5 text-blue-500" />
            </div>
            <div className="text-lg font-bold text-gray-800">
              {playersCount}
            </div>
            <p className="text-xs text-gray-600">Players</p>
          </div>
        </div>
        
        <div className="card p-4 text-center">
          <div className="space-y-2">
            <div className="flex items-center justify-center">
              <Zap className="h-5 w-5 text-purple-500" />
            </div>
            <div className="text-lg font-bold text-gray-800">
              {totalQuestions}
            </div>
            <p className="text-xs text-gray-600">Rounds</p>
          </div>
        </div>
      </div>

      {/* Progress Section */}
      {totalQuestions > 0 && (
        <div className="card p-6">
          <div className="space-y-4">
            <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-blue-500" />
              <span>Performance</span>
            </h4>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Accuracy</span>
                  <span>{accuracy}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${accuracy}%` }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{Math.min(totalQuestions * 10, 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(totalQuestions * 10, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tips Card */}
      <div className="card p-6 bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
            <Zap className="h-4 w-4 text-purple-500" />
            <span>Pro Tips</span>
          </h4>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• Look for distinctive facial features</p>
            <p>• Pay attention to eye shapes and nose structure</p>
            <p>• Consider the overall face shape</p>
            <p>• Upload clear, front-facing photos for best results</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsSection;