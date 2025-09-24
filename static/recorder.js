// Advanced audio recorder using Web Audio API
class AudioRecorder {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.mediaStreamSource = null;
        this.processor = null;
        this.recording = false;
        this.audioBuffers = [];
        this.sampleRate = 44100;
    }

    async startRecording() {
        try {
            // Get microphone access
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.sampleRate = this.audioContext.sampleRate;
            
            // Create media stream source
            this.mediaStreamSource = this.audioContext.createMediaStreamSource(this.mediaStream);
            
            // Create script processor (deprecated but works everywhere)
            const bufferSize = 4096;
            this.processor = this.audioContext.createScriptProcessor(bufferSize, 1, 1);
            
            // Reset buffers
            this.audioBuffers = [];
            this.recording = true;
            
            // Process audio
            this.processor.onaudioprocess = (e) => {
                if (!this.recording) return;
                
                const inputBuffer = e.inputBuffer;
                const inputData = inputBuffer.getChannelData(0);
                
                // Clone the data and store it
                const buffer = new Float32Array(inputData);
                this.audioBuffers.push(buffer);
                
                // Log progress every 10 chunks
                if (this.audioBuffers.length % 10 === 0) {
                    console.log('Recording progress: ' + this.audioBuffers.length + ' chunks');
                }
            };
            
            // Connect nodes
            this.mediaStreamSource.connect(this.processor);
            this.processor.connect(this.audioContext.destination);
            
            console.log('Recording started with Web Audio API');
            return true;
            
        } catch (error) {
            console.error('Failed to start recording:', error);
            throw error;
        }
    }

    stopRecording() {
        this.recording = false;
        
        // Disconnect nodes
        if (this.processor) {
            this.processor.disconnect();
            this.processor = null;
        }
        
        if (this.mediaStreamSource) {
            this.mediaStreamSource.disconnect();
            this.mediaStreamSource = null;
        }
        
        // Stop media stream
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
        
        // Close audio context
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        
        console.log('Recording stopped, buffers collected: ' + this.audioBuffers.length);
        
        // Convert to WAV
        if (this.audioBuffers.length > 0) {
            const wavBlob = this.createWAVBlob();
            console.log('WAV blob created, size: ' + wavBlob.size);
            return wavBlob;
        }
        
        return null;
    }

    createWAVBlob() {
        // Merge all buffers
        const totalLength = this.audioBuffers.reduce((acc, buffer) => acc + buffer.length, 0);
        const mergedBuffer = new Float32Array(totalLength);
        
        let offset = 0;
        for (const buffer of this.audioBuffers) {
            mergedBuffer.set(buffer, offset);
            offset += buffer.length;
        }
        
        // Convert float32 to int16
        const length = mergedBuffer.length;
        const buffer = new ArrayBuffer(44 + length * 2);
        const view = new DataView(buffer);
        
        // WAV header
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };
        
        writeString(0, 'RIFF');
        view.setUint32(4, 36 + length * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true); // fmt chunk size
        view.setUint16(20, 1, true); // PCM format
        view.setUint16(22, 1, true); // Mono
        view.setUint32(24, this.sampleRate, true);
        view.setUint32(28, this.sampleRate * 2, true); // byte rate
        view.setUint16(32, 2, true); // block align
        view.setUint16(34, 16, true); // bits per sample
        writeString(36, 'data');
        view.setUint32(40, length * 2, true);
        
        // Convert float32 to int16
        let index = 44;
        for (let i = 0; i < length; i++) {
            const sample = Math.max(-1, Math.min(1, mergedBuffer[i]));
            view.setInt16(index, sample * 0x7FFF, true);
            index += 2;
        }
        
        return new Blob([buffer], { type: 'audio/wav' });
    }
}

// Export for use in HTML
window.AudioRecorder = AudioRecorder;
