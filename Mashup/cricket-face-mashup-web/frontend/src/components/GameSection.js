import React from 'react';
import { Shuffle, Clock, Trophy, Zap, Play } from 'lucide-react';

const GameSection = ({
  currentMashup,
  quizOptions,
  onAnswer,
  gameMode,
  isLoading,
  onNextRound
}) => {
  
  if (!currentMashup && gameMode === 'playing') {
    return (
      <div className="card p-8 text-center">
        <div className="animate-spin w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full mx-auto mb-4"></div>
        <p className="text-lg text-gray-600">Creating your mashup challenge...</p>
      </div>
    );
  }

  if (!currentMashup) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Mashup Display */}
      <div className="card overflow-hidden">
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <Zap className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Cricket Face Mashup</h2>
                <p className="text-blue-100">Can you identify the blended players?</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-blue-100">Challenge</div>
              <div className="text-lg font-bold">#{Math.random().toString(36).substr(2, 6).toUpperCase()}</div>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <div className="relative">
            <div className="aspect-square w-full max-w-sm mx-auto bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl overflow-hidden shadow-lg">
              {currentMashup.mashup_image ? (
                <img
                  src={currentMashup.mashup_image}
                  alt="Blended cricket players"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="animate-pulse">
                      <div className="w-20 h-20 bg-gray-300 rounded-full mx-auto mb-4"></div>
                      <div className="h-4 bg-gray-300 rounded w-3/4 mx-auto"></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {currentMashup.used_players && (
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-500">
                Blended from {currentMashup.used_players.length} cricket players
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Quiz Options */}
      {quizOptions.length > 0 && (
        <div className="card p-6">
          <div className="space-y-4">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Who are the players in this mashup?
              </h3>
              <p className="text-sm text-gray-600">
                Select the correct combination of cricket players
              </p>
            </div>
            
            <div className="grid grid-cols-1 gap-3">
              {quizOptions.map((option, index) => (
                <button
                  key={index}
                  onClick={() => onAnswer(option)}
                  disabled={gameMode === 'answered'}
                  className={`
                    p-4 text-left rounded-lg border-2 transition-all duration-200 
                    ${gameMode === 'answered' 
                      ? 'cursor-not-allowed opacity-60' 
                      : 'hover:border-blue-400 hover:bg-blue-50 cursor-pointer'
                    }
                    border-gray-200 bg-white hover:shadow-md
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-sm font-medium text-gray-600">
                        {String.fromCharCode(65 + index)}
                      </div>
                      <span className="font-medium text-gray-800">{option}</span>
                    </div>
                    <div className="text-blue-500">
                      {gameMode === 'playing' && <Play className="h-4 w-4" />}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Next Round Button */}
      {gameMode === 'answered' && (
        <div className="card p-6 text-center">
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-2">
              <Trophy className="h-6 w-6 text-yellow-500" />
              <h3 className="text-lg font-semibold text-gray-800">
                Round Complete!
              </h3>
            </div>
            <p className="text-gray-600">
              Ready for the next challenge?
            </p>
            <button
              onClick={onNextRound}
              disabled={isLoading}
              className="btn-primary px-6 py-3 inline-flex items-center space-x-2"
            >
              <Shuffle className="h-5 w-5" />
              <span>{isLoading ? 'Creating Next Mashup...' : 'Next Round'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameSection;