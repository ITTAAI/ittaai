import React, { useEffect, useRef, useState } from 'react';
import { KeyboardVoiceOutlined, MicOffOutlined } from "@mui/icons-material";
import { IconButton } from "@mui/material";
import { useRecoilState } from "recoil";
import { captionState } from "./states/captionState.ts";

const SEND_INTERVAL = 15000; // 15 seconds

const Audio: React.FC = () => {
    const [recording, setRecording] = useState<boolean>(false);
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const ws = useRef<WebSocket | null>(null);
    const audioChunks = useRef<Blob[]>([]);
    const [, setCaption] = useRecoilState(captionState);
    const intervalRef = useRef<number | null>(null); // Changed type to 'number | null'

    const sendData = () => {
        if (audioChunks.current.length === 0) return;

        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(audioBlob);
        }

        audioChunks.current = [];
    };

    const startRecording = async () => {
        console.log("Connecting to WS server and starting recording");

        // Close any existing WebSocket connection
        if (ws.current) {
            ws.current.close();
        }

        // Create a new WebSocket connection
        ws.current = new WebSocket("ws://localhost:8000/ws");

        ws.current.onopen = async () => {
            console.log("Connected to the WS server");

            // Now that we are connected to WebSocket, start recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

                mediaRecorder.current = new MediaRecorder(stream);

                mediaRecorder.current.ondataavailable = event => {
                    audioChunks.current.push(event.data);
                };

                mediaRecorder.current.onstop = sendData;

                mediaRecorder.current.start();
                setRecording(true);

                // Set an interval to send data every SEND_INTERVAL ms
                intervalRef.current = window.setInterval(() => { // Used window.setInterval
                    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
                        mediaRecorder.current.stop();
                        mediaRecorder.current.start();
                    }
                }, SEND_INTERVAL);
            } catch (err) {
                console.error("Error accessing audio:", err);
            }
        };

        ws.current.onerror = (error: Event) => {
            console.error("WebSocket Error:", error);
        };

        ws.current.onmessage = (event: MessageEvent) => {
            const cleanedData = event.data.replace(/\n/g, ' '); // Replace all newline characters with a space
            setCaption((prevCaption) => ({
                value: `${prevCaption.value} ${cleanedData}`
            }));
        };

        ws.current.onclose = (event) => {
            console.log(`WebSocket closed: ${event.code} ${event.reason}`);
            setRecording(false);
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    };

    const stopRecording = () => {
        if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
            mediaRecorder.current.stop();
        }

        if (ws.current) {
            ws.current.close();
        }

        if (intervalRef.current) {
            clearInterval(intervalRef.current); // Clear the interval on stop
            intervalRef.current = null; // Reset the ref to null
        }
    };

    useEffect(() => {
        // Cleanup on component unmount
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null; // Reset the ref to null
            }

            if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
                mediaRecorder.current.stop();
            }

            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    return (
        <div>
            {!recording &&
                <IconButton onClick={startRecording}>
                    <KeyboardVoiceOutlined />
                </IconButton>
            }
            {recording &&
                <IconButton onClick={stopRecording}>
                    <MicOffOutlined />
                </IconButton>
            }
        </div>
    );
}

export default Audio;
