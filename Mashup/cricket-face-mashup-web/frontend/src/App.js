import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Trophy, Upload, Shuffle, Users, Zap } from 'lucide-react';
import axios from 'axios';
import GameSection from './components/GameSection';
import StatsSection from './components/StatsSection';

const API_BASE = 'http://localhost:8001';

function App() {
  const [players, setPlayers] = useState([]);
  const [gameState, setGameState] = useState('loading');
  const [currentMashup, setCurrentMashup] = useState(null);
  const [quizOptions, setQuizOptions] = useState([]);
  const [correctAnswer, setCorrectAnswer] = useState('');
  const [score, setScore] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [gameMode, setGameMode] = useState('answered');

  const [stats, setStats] = useState({
    accuracy: 0,
    bestStreak: 0,
    currentStreak: 0,
    avgTime: 0
  });

  useEffect(() => {
    checkPreloadedPlayers();
  }, []);

  const checkPreloadedPlayers = async () => {
    try {
      const response = await axios.get(`${API_BASE}/players`);
      
      if (response.data.players && response.data.players.length > 0) {
        setPlayers(response.data.players);
        setGameState('ready');
        toast.success(`🎯 Ready to play with ${response.data.players.length} preloaded cricket players!`, {
          icon: '🏏',
        });
      } else {
        setGameState('upload');
        toast.error('No preloaded players found.');
      }
    } catch (error) {
      console.error('Backend connection error:', error);
      toast.error('❌ Backend connection failed. Make sure the server is running.');
      setGameState('upload');
    }
  };

  const startNewRound = async () => {
    if (players.length < 3) {
      toast.error('Need at least 3 players to start the game!');
      return;
    }

    setIsLoading(true);
    setGameMode('playing');

    try {
      const mashupResponse = await axios.post(`${API_BASE}/create-mashup`);

      if (mashupResponse.data.success) {
        setCurrentMashup(mashupResponse.data);

        const quizResponse = await axios.post(`${API_BASE}/generate-quiz`, {
          correct_players: mashupResponse.data.used_players,
          total_options: 4
        });

        if (quizResponse.data.success) {
          setQuizOptions(quizResponse.data.options);
          setCorrectAnswer(quizResponse.data.correct_answer);
          setGameState('playing');
          toast.success('New mashup created! Can you guess the players?', {
            icon: '🎯',
          });
        }
      }
    } catch (error) {
      console.error('Error creating mashup:', error);
      toast.error('Failed to create mashup. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswer = (selectedAnswer) => {
    const isCorrect = selectedAnswer === correctAnswer;
    setTotalQuestions(prev => prev + 1);
    
    if (isCorrect) {
      setScore(prev => prev + 1);
      setStats(prev => ({
        ...prev,
        currentStreak: prev.currentStreak + 1,
        bestStreak: Math.max(prev.bestStreak, prev.currentStreak + 1)
      }));
      toast.success('Correct! Well done! 🎉', {
        icon: '✅',
      });
    } else {
      setStats(prev => ({
        ...prev,
        currentStreak: 0
      }));
      toast.error(`Wrong! Correct answer: ${correctAnswer}`, {
        icon: '❌',
      });
    }

    const newAccuracy = totalQuestions > 0 ? 
      Math.round(((isCorrect ? score + 1 : score) / (totalQuestions + 1)) * 100) : 0;
    setStats(prev => ({ ...prev, accuracy: newAccuracy }));

    setGameMode('answered');
  };

  if (gameState === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
          <h2 className="text-2xl font-bold text-gray-800">Loading Cricket Face Mashup</h2>
          <p className="text-gray-600">Checking for preloaded cricket players...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#ffffff',
            color: '#374151',
            borderRadius: '12px',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          },
        }}
      />
      
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-cricket-blue">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl shadow-lg">
                <Trophy className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                  Cricket Face Mashup Challenge
                </h1>
                <p className="text-gray-600 mt-1">Test your cricket knowledge!</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Users className="h-4 w-4" />
                <span>{players.length} Players Preloaded</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            {gameState === 'ready' ? (
              <div className="space-y-6">
                <div className="card p-6 text-center bg-gradient-to-br from-green-50 to-blue-50">
                  <div className="space-y-4">
                    <div className="flex items-center justify-center space-x-2">
                      <Zap className="h-6 w-6 text-yellow-500" />
                      <h3 className="text-xl font-semibold text-gray-800">Ready to Play!</h3>
                    </div>
                    <p className="text-gray-600">Cricket players preloaded and ready for mashup!</p>
                    <button
                      onClick={startNewRound}
                      disabled={isLoading}
                      className="btn-primary px-8 py-3 text-lg inline-flex items-center space-x-2"
                    >
                      <Shuffle className="h-5 w-5" />
                      <span>{isLoading ? 'Creating Mashup...' : 'Start First Round'}</span>
                    </button>
                  </div>
                </div>
                
                {/* Show preloaded players */}
                <div className="card p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
                    <Users className="h-5 w-5 text-green-500" />
                    <span>Preloaded Players ({players.length})</span>
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {players.map((player, index) => (
                      <div key={index} className="text-center space-y-2">
                        <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                          <img
                            src={player.image_url}
                            alt={player.name}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <p className="text-xs font-medium text-gray-700 truncate">{player.name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <GameSection
                currentMashup={currentMashup}
                quizOptions={quizOptions}
                onAnswer={handleAnswer}
                gameMode={gameMode}
                isLoading={isLoading}
                onNextRound={startNewRound}
              />
            )}
          </div>

          <div className="lg:col-span-1">
            <StatsSection
              score={score}
              totalQuestions={totalQuestions}
              stats={stats}
              playersCount={players.length}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;