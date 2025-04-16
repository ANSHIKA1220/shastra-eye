import { useEffect, useState, useRef } from "react";
import { AlertTriangle, History, Volume2, VolumeX, Sun, Moon, Maximize2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "react-tabs";
import useSound from "use-sound";

export default function App() {
  const [frame, setFrame] = useState(null);
  const [threats, setThreats] = useState([]);
  const [logs, setLogs] = useState([]);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const [muted, setMuted] = useState(false);
  const ws = useRef(null);
  const videoRef = useRef(null);
  const [play] = useSound("/alert.mp3", { soundEnabled: !muted });

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then((devs) => {
      const videoDevices = devs.filter((d) => d.kind === "videoinput");
      setDevices(videoDevices);
      if (videoDevices[0]) setSelectedDevice(videoDevices[0].deviceId);
    });
  }, []);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch("http://localhost:8000/alerts/logs");
        if (!response.ok) throw new Error("Failed to fetch logs");
        const data = await response.json();
        setLogs(data);
      } catch (error) {
        console.error("Error fetching logs:", error);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!selectedDevice) return;
    if (ws.current) ws.current.close();
    ws.current = new WebSocket(`ws://localhost:8000/video/ws?deviceId=${selectedDevice}`); // Changed to 8000
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setFrame(`data:image/jpeg;base64,${data.image}`);
        setThreats(data.threats);
        if (data.threats.length > 0) play();
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };
    ws.current.onerror = () => console.error("WebSocket error");
    return () => ws.current?.close();
  }, [selectedDevice, play]);

  const toggleFullscreen = () => {
    const el = videoRef.current;
    if (!document.fullscreenElement) {
      if (el.requestFullscreen) el.requestFullscreen();
    } else if (document.exitFullscreen) document.exitFullscreen();
  };

  return (
    <div className={`min-h-screen transition-all duration-300 ${darkMode ? "bg-gradient-to-tr from-black via-zinc-900 to-black text-white" : "bg-gray-100 text-black"}`}>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 p-4">
        <h1 className="text-3xl font-bold animate-fade-in">Threat Detection Dashboard</h1>
        <div className="flex gap-4 flex-wrap items-center">
          <select
            className="bg-zinc-800 text-white rounded px-3 py-1 hover:bg-zinc-700 transition"
            value={selectedDevice || ""}
            onChange={(e) => setSelectedDevice(e.target.value)}
          >
            <option value="">Select Camera</option>
            {devices.map((device) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `Camera ${device.deviceId.slice(0, 8)}`}
              </option>
            ))}
          </select>
          <button
            onClick={() => setMuted(!muted)}
            className="p-2 rounded-full hover:bg-zinc-700 transition"
          >
            {muted ? <VolumeX className="text-red-400" /> : <Volume2 className="text-green-400" />}
          </button>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-full hover:bg-zinc-700 transition"
          >
            {darkMode ? <Sun className="text-yellow-400" /> : <Moon className="text-zinc-800" />}
          </button>
        </div>
      </div>

      <div className="p-4">
        <div className="bg-zinc-800 rounded-lg mb-4">
          <button
            className="px-4 py-2 text-white hover:bg-zinc-700"
            onClick={() => {/* Simulate tab switch */}}
          >
            Live View
          </button>
          <button
            className="px-4 py-2 text-white hover:bg-zinc-700"
            onClick={() => {/* Simulate tab switch */}}
          >
            Threat Log
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-zinc-900 shadow-2xl rounded-2xl animate-slide-up p-4">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-2xl font-bold">Live Feed</h2>
              <button
                onClick={toggleFullscreen}
                className="p-2 hover:bg-zinc-700 rounded-full transition"
              >
                <Maximize2 className="text-gray-400" />
              </button>
            </div>
            <div ref={videoRef} className="w-full">
              {frame ? (
                <img
                  src={frame}
                  alt="Live camera"
                  className="rounded-xl w-full border-4 border-zinc-800 transition-all duration-200"
                />
              ) : (
                <p className="text-zinc-500 animate-pulse">Waiting for camera input...</p>
              )}
            </div>
          </div>

          <div className="bg-zinc-900 shadow-2xl rounded-2xl animate-slide-up p-4">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <AlertTriangle className="text-yellow-400" /> Detected Threats
            </h2>
            <div className="h-64 overflow-y-auto">
              {threats.length > 0 ? (
                threats.map((t, i) => (
                  <span
                    key={i}
                    className="bg-red-600 text-white m-1 text-lg px-3 py-1 rounded-full animate-pulse inline-block"
                  >
                    {t.toUpperCase()}
                  </span>
                ))
              ) : (
                <p className="text-green-400">No threats detected</p>
              )}
            </div>
          </div>
        </div>

        <div className="mt-4">
          <div className="bg-zinc-900 shadow-2xl rounded-2xl animate-slide-up p-4">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <History className="text-blue-400" /> Threat History
            </h2>
            <div className="h-72 overflow-y-auto">
              {logs.length > 0 ? (
                logs.map((log, i) => (
                  <div key={log.id} className="mb-4 border-b border-zinc-700 pb-2 animate-fade-in">
                    <p className="text-sm text-zinc-400 mb-1">
                      {new Date(log.timestamp).toLocaleString()}
                    </p>
                    <div className="flex gap-2 flex-wrap">
                      {log.threats.map((t, j) => (
                        <span
                          key={j}
                          className="bg-red-500 text-white text-sm px-2 py-1 rounded-full"
                        >
                          {t.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-zinc-500">No threat history available</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}