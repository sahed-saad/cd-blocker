import { useState, useEffect, useRef } from 'react';

function Product() {
  const [isConnected, setIsConnected] = useState(false);
  const [cardDetected, setCardDetected] = useState(false);
  const [detectionStatus, setDetectionStatus] = useState({});
  const [connectionError, setConnectionError] = useState(null);
  const [currentFrame, setCurrentFrame] = useState(null);
  
  const wsRef = useRef(null);
  const canvasRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  
  const WEBSOCKET_URL = 'ws://localhost:8765';
  const RECONNECT_DELAY = 3000;

  const connectWebSocket = () => {
    try {
      setConnectionError(null);
      const ws = new WebSocket(WEBSOCKET_URL);
      
      ws.onopen = () => {
        console.log('✅ Connected to credit card detection server');
        setIsConnected(true);
        setConnectionError(null);
        
        // Request initial status
        ws.send(JSON.stringify({ type: 'get_status' }));
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'video_frame':
              setCurrentFrame(data.frame);
              setCardDetected(data.card_detected);
              break;
              
            case 'detection_status':
              setDetectionStatus({
                cardDetected: data.card_detected,
                requestCount: data.request_count,
                maxRequests: data.max_requests,
                nextCheck: data.next_check,
                timestamp: data.timestamp
              });
              setCardDetected(data.card_detected);
              break;
              
            case 'connection':
              console.log('📡 Server message:', data.message);
              break;
              
            default:
              console.log('📨 Received:', data);
          }
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };
      
      ws.onclose = (event) => {
        console.log('🔌 WebSocket connection closed:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;
        
        // Attempt to reconnect if not a manual close
        if (event.code !== 1000) {
          setConnectionError('Connection lost. Attempting to reconnect...');
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, RECONNECT_DELAY);
        }
      };
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setConnectionError('Failed to connect to detection server');
        setIsConnected(false);
      };
      
      wsRef.current = ws;
      
    } catch (error) {
      console.error('❌ Error creating WebSocket connection:', error);
      setConnectionError('Failed to create connection to detection server');
    }
  };

  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  };

  const sendCommand = (command) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: command }));
    }
  };

  // Draw frame on canvas
  useEffect(() => {
    if (currentFrame && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
      };
      
      img.src = `data:image/jpeg;base64,${currentFrame}`;
    }
  }, [currentFrame]);

  // Initialize WebSocket connection
  useEffect(() => {
    connectWebSocket();
    
    return () => {
      disconnect();
    };
  }, []);

  const formatTime = (seconds) => {
    return seconds > 0 ? `${seconds}s` : 'Now';
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-green-400 mb-2">
            🛡️ Credit Card Detection System
          </h1>
          <p className="text-gray-300">
            Real-time payment card detection with automatic screen protection
          </p>
        </div>

        {/* Connection Status */}
        <div className="mb-6 p-4 rounded-lg border-2 border-gray-700 bg-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full ${
                isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}></div>
              <span className="text-lg font-semibold">
                {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
            </div>
            
            <div className="flex space-x-2">
              {!isConnected && (
                <button
                  onClick={connectWebSocket}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
                >
                  🔄 Reconnect
                </button>
              )}
              {isConnected && (
                <button
                  onClick={disconnect}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors"
                >
                  🔌 Disconnect
                </button>
              )}
            </div>
          </div>
          
          {connectionError && (
            <div className="mt-2 text-red-400">
              ⚠️ {connectionError}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video Stream */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg p-4 border-2 border-gray-700">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                📹 Live Camera Stream
                {cardDetected && (
                  <span className="ml-3 px-3 py-1 bg-red-600 text-white rounded-full text-sm animate-pulse">
                    🚨 CARD DETECTED
                  </span>
                )}
              </h2>
              
              <div className="relative bg-black rounded-lg overflow-hidden">
                {currentFrame ? (
                  <canvas
                    ref={canvasRef}
                    className="w-full h-auto max-w-full"
                    style={{ aspectRatio: '16/9' }}
                  />
                ) : (
                  <div className="aspect-video flex items-center justify-center text-gray-400">
                    {isConnected ? (
                      <div className="text-center">
                        <div className="animate-spin text-4xl mb-2">⏳</div>
                        <p>Loading camera stream...</p>
                      </div>
                    ) : (
                      <div className="text-center">
                        <div className="text-4xl mb-2">📹</div>
                        <p>Connect to view camera stream</p>
                      </div>
                    )}
                  </div>
                )}
                
                {cardDetected && (
                  <div className="absolute top-4 left-4 right-4 text-center">
                    <div className="bg-red-600 text-white px-4 py-2 rounded-lg font-bold animate-pulse">
                      ⚠️ PAYMENT CARD DETECTED - SCREEN PROTECTED ⚠️
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Controls and Status */}
          <div className="space-y-6">
            {/* Detection Status */}
            <div className="bg-gray-800 rounded-lg p-4 border-2 border-gray-700">
              <h3 className="text-lg font-bold mb-4 text-green-400">
                📊 Detection Status
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>🎯 Card Status:</span>
                  <span className={`font-bold ${
                    cardDetected ? 'text-red-400' : 'text-green-400'
                  }`}>
                    {cardDetected ? 'DETECTED' : 'NOT DETECTED'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span>🤖 API Calls:</span>
                  <span className="font-mono">
                    {detectionStatus.requestCount || 0}/{detectionStatus.maxRequests || 500}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span>⏱️ Next Check:</span>
                  <span className="font-mono">
                    {formatTime(detectionStatus.nextCheck || 0)}
                  </span>
                </div>
                
                {detectionStatus.timestamp && (
                  <div className="text-xs text-gray-400 mt-2">
                    Last update: {new Date(detectionStatus.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>

            {/* Controls */}
            <div className="bg-gray-800 rounded-lg p-4 border-2 border-gray-700">
              <h3 className="text-lg font-bold mb-4 text-blue-400">
                🎮 Controls
              </h3>
              
              <div className="space-y-3">
                <button
                  onClick={() => sendCommand('force_check')}
                  disabled={!isConnected}
                  className="w-full px-4 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
                >
                  🔍 Force Check Now
                </button>
                
                <button
                  onClick={() => sendCommand('clear_detection')}
                  disabled={!isConnected || !cardDetected}
                  className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
                >
                  🔄 Clear Detection
                </button>
                
                <button
                  onClick={() => sendCommand('get_status')}
                  disabled={!isConnected}
                  className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
                >
                  📊 Refresh Status
                </button>
              </div>
            </div>

            {/* System Info */}
            <div className="bg-gray-800 rounded-lg p-4 border-2 border-gray-700">
              <h3 className="text-lg font-bold mb-4 text-purple-400">
                ℹ️ System Info
              </h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Detection Interval:</span>
                  <span className="font-mono">6 seconds</span>
                </div>
                <div className="flex justify-between">
                  <span>Stream Quality:</span>
                  <span className="font-mono">15 FPS</span>
                </div>
                <div className="flex justify-between">
                  <span>Protection Mode:</span>
                  <span className="font-mono">Full Screen Blur</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6 border-2 border-gray-700">
          <h3 className="text-xl font-bold mb-4 text-cyan-400">
            📋 How It Works
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="text-center p-4 bg-gray-700 rounded-lg">
              <div className="text-2xl mb-2">🎥</div>
              <h4 className="font-bold mb-2">Live Monitoring</h4>
              <p className="text-gray-300">
                Camera continuously streams to detect payment cards in real-time
              </p>
            </div>
            <div className="text-center p-4 bg-gray-700 rounded-lg">
              <div className="text-2xl mb-2">🤖</div>
              <h4 className="font-bold mb-2">AI Detection</h4>
              <p className="text-gray-300">
                Gemini AI analyzes frames every 6 seconds for credit cards
              </p>
            </div>
            <div className="text-center p-4 bg-gray-700 rounded-lg">
              <div className="text-2xl mb-2">🛡️</div>
              <h4 className="font-bold mb-2">Auto Protection</h4>
              <p className="text-gray-300">
                Entire screen blurs automatically when cards are detected
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Product;