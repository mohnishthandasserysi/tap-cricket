import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Trophy, Upload, Shuffle, Users, Zap, RefreshCw } from 'lucide-react';
import axios from 'axios';
import UploadSection from './components/UploadSection';
import GameSection from './components/GameSection';
import StatsSection from './components/StatsSection';

const API_BASE = 'http://localhost:8001';  // CHANGED TO PORT 8001

function App() {
  const [players, setPlayers] = useState([]);
  const [gameState, setGameState] = useState('upload'); // 'loading', 'upload', 'playing'
  const [currentMashup, setCurrentMashup] = useState(null);
  const [quizOptions, setQuizOptions] = useState([]);
  const [correctAnswer, setCorrectAnswer] = useState('');
  const [score, setScore] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [gameMode, setGameMode] = useState('answered'); // 'playing', 'answered'

  const [stats, setStats] = useState({
    accuracy: 0,
    bestStreak: 0,
    currentStreak: 0,
    avgTime: 0
  });

  const handleUploadComplete = (uploadedPlayers) => {
    setPlayers(uploadedPlayers);
    setGameState('ready');
    toast.success(`Uploaded ${uploadedPlayers.length} players! Ready to play!`, {
      icon: '🏏',
    });
  };

  const startNewRound = async () => {
    if (players.length < 3) {
      toast.error('Need at least 3 players to start the game!');
      return;
    }

    setIsLoading(true);
    setGameMode('playing');

    try {
      const mashupResponse = await axios.post(`${API_BASE}/create-mashup`, null, {
        params: { num_players: 3 }
      });

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
                <p className="text-gray-600 mt-1">Guess the blended cricket legends! (Fast Mode - Port 8001)</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            {gameState === 'upload' ? (
              <UploadSection onUploadComplete={handleUploadComplete} />
            ) : gameState === 'ready' ? (
              <div className="card p-6 text-center bg-gradient-to-br from-green-50 to-blue-50">
                <div className="space-y-4">
                  <div className="flex items-center justify-center space-x-2">
                    <Zap className="h-6 w-6 text-yellow-500" />
                    <h3 className="text-xl font-semibold text-gray-800">Ready to Play!</h3>
                  </div>
                  <p className="text-gray-600">You have {players.length} cricket players loaded.</p>
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
