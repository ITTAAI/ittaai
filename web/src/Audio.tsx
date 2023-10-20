import React, {useEffect, useRef, useState} from 'react';
import {Button} from "@mui/material";

const CHUNK_SIZE = 1024; // 根据实际需要调整这个值

const Audio: React.FC = () => {
    const [recording, setRecording] = useState<boolean>(false);
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const audioChunks = useRef<Blob[]>([]);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        ws.current = new WebSocket("ws://localhost:8000/ws");

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

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({audio: true});
            mediaRecorder.current = new MediaRecorder(stream);

            mediaRecorder.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.current.push(event.data);
                }

                if (audioChunks.current.length >= CHUNK_SIZE) {
                    sendAudioChunks();
                }
            };

            mediaRecorder.current.onstop = () => {
                if (audioChunks.current.length > 0) {
                    sendAudioChunks();
                }
            };

            mediaRecorder.current.start();
            setRecording(true);
        } catch (err) {
            console.error("Error accessing audio:", err);
        }
    };

    const stopRecording = () => {
        if (mediaRecorder.current) {
            mediaRecorder.current.stop();
            setRecording(false);
        }
    };

    const sendAudioChunks = () => {
        const blob = new Blob(audioChunks.current, {type: 'audio/wav'});
        const reader = new FileReader();

        reader.onloadend = () => {
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                ws.current.send(reader.result as ArrayBuffer);
            }
        }
        reader.readAsArrayBuffer(blob);

        audioChunks.current = [];
    };

    return (
        <div>
            {!recording && <Button onClick={startRecording}>Start Recording</Button>}
            {recording && <Button onClick={stopRecording}>Stop Recording</Button>}
        </div>
    );
}

export default Audio;
