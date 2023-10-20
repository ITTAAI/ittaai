import React, {useEffect, useRef, useState} from 'react';

const SEND_INTERVAL = 1000; // 每秒发送一次

const Audio: React.FC = () => {
  const [recording, setRecording] = useState<boolean>(false);
  const audioContext = useRef<AudioContext | null>(null);
  const processor = useRef<ScriptProcessorNode | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const audioDataBuffer = useRef<Int16Array[]>([]); // 用于存储音频数据直到发送

  useEffect(() => {
    ws.current = new WebSocket("YOUR_WS_SERVER_URL");

    ws.current.onopen = () => {
      console.log("Connected to the WS server");
    };

    ws.current.onerror = (error: Event) => {
      console.error("WebSocket Error:", error);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const sendData = () => {
    if (audioDataBuffer.current.length === 0) return;

    // Calculate the total length of the concatenated buffer.
    const totalLength = audioDataBuffer.current.reduce((acc, curr) => acc + curr.length, 0);

    // Create a new buffer to hold all the data.
    const concatenatedBuffer = new Int16Array(totalLength);

    // Fill the new buffer with the data.
    let offset = 0;
    for (let buffer of audioDataBuffer.current) {
      concatenatedBuffer.set(buffer, offset);
      offset += buffer.length;
    }

    // Now you have a single Int16Array containing all the data.
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(concatenatedBuffer.buffer);
    }

    audioDataBuffer.current = [];
  };


  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio: true});

      audioContext.current = new AudioContext();
      const source = audioContext.current.createMediaStreamSource(stream);
      processor.current = audioContext.current.createScriptProcessor(4096, 1, 1);

      processor.current.onaudioprocess = (event) => {
        if (!recording) return;

        const channelData = event.inputBuffer.getChannelData(0);
        const buffer = new Int16Array(channelData.length);
        for (let i = 0; i < channelData.length; i++) {
          buffer[i] = Math.min(1, channelData[i]) * 0x7FFF;
        }
        audioDataBuffer.current.push(buffer);
      };

      source.connect(processor.current);
      processor.current.connect(audioContext.current.destination);

      setRecording(true);

      // 每秒发送一次
      const interval = setInterval(sendData, SEND_INTERVAL);
      return () => clearInterval(interval);

    } catch (err) {
      console.error("Error accessing audio:", err);
    }
  };

  const stopRecording = () => {
    if (audioContext.current && processor.current) {
      processor.current.disconnect(audioContext.current.destination);
      audioContext.current.close();
      setRecording(false);
    }
    sendData(); // 发送最后的数据
  };

  return (
      <div>
        {!recording && <button onClick={startRecording}>Start Recording</button>}
        {recording && <button onClick={stopRecording}>Stop Recording</button>}
      </div>
  );
}

export default Audio;
