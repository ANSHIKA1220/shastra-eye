import { useEffect, useState, useRef } from "react";
import { AlertTriangle, History, Volume2, VolumeX, Sun, Moon, Maximize2 } from "lucide-react";
import useSound from "use-sound";
import { Button } from "@/components/ui/button";

export default function CameraPage() {
  const [frame, setFrame] = useState<string | null>(null);
  const [threats, setThreats] = useState<string[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(true);
  const [muted, setMuted] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const videoRef = useRef<HTMLDivElement | null>(null);
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
    ws.current = new WebSocket(`ws://localhost:8000/video/ws?deviceId=${selectedDevice}`);
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
      if (el?.requestFullscreen) el.requestFullscreen();
    } else if (document.exitFullscreen) document.exitFullscreen();
  };

  return (
    <div className={`min-h-screen transition-all duration-300 ${darkMode ? "bg-shastra-navy text-foreground" : "bg-gray-100 text-black"}`}>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 p-6 screen-glow">
        <h1 className="text-4xl font-bold terminal-text animate-fade-in">Threat Detection Dashboard</h1>
        <div className="flex gap-4 flex-wrap items-center">
          <select
            className="glassmorphism text-white rounded px-3 py-2 control-button"
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
          <Button
            variant="outline"
            className="control-button"
            onClick={() => setMuted(!muted)}
          >
            {muted ? <VolumeX className="text-red-400" /> : <Volume2 className="text-green-400" />}
          </Button>
          <Button
            variant="outline"
            className="control-button"
            onClick={() => setDarkMode(!darkMode)}
          >
            {darkMode ? <Sun className="text-yellow-400" /> : <Moon className="text-zinc-800" />}
          </Button>
        </div>
      </div>

      <div className="p-6">
        <div className="flex space-x-4 mb-6">
          <Button className="control-button">Live View</Button>
          <Button className="control-button">Threat Log</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="neon-box p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-3xl font-bold terminal-text">Live Feed</h2>
              <Button
                variant="outline"
                className="control-button"
                onClick={toggleFullscreen}
              >
                <Maximize2 className="text-gray-400" />
              </Button>
            </div>
            <div ref={videoRef} className="w-full">
              {frame ? (
                <img
                  src={frame}
                  alt="Live camera"
                  className="rounded-md w-full border-4 border-shastra-cyan/50"
                />
              ) : (
                <p className="text-muted-foreground animate-pulse">Waiting for camera input...</p>
              )}
            </div>
          </div>

          <div className="neon-box p-6">
            <h2 className="text-3xl font-bold terminal-text mb-4 flex items-center gap-2">
              <AlertTriangle className="text-yellow-400" /> Detected Threats
            </h2>
            <div className="h-64 overflow-y-auto">
              {threats.length > 0 ? (
                threats.map((t, i) => (
                  <span
                    key={i}
                    className="bg-destructive text-destructive-foreground m-1 text-lg px-3 py-1 rounded-full animate-pulse inline-block"
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

        <div className="mt-6">
          <div className="neon-box p-6">
            <h2 className="text-3xl font-bold terminal-text mb-4 flex items-center gap-2">
              <History className="text-blue-400" /> Threat History
            </h2>
            <div className="h-72 overflow-y-auto">
              {logs.length > 0 ? (
                logs.map((log, i) => (
                  <div key={log.id} className="mb-4 border-b border-shastra-cyan/20 pb-2 animate-fade-in">
                    <p className="text-sm text-muted-foreground mb-1">
                      {new Date(log.timestamp).toLocaleString()}
                    </p>
                    <div className="flex gap-2 flex-wrap">
                      {log.threats.map((t, j) => (
                        <span
                          key={j}
                          className="bg-destructive text-destructive-foreground text-sm px-2 py-1 rounded-full"
                        >
                          {t.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">No threat history available</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}