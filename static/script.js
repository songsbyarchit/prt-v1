// Get references to HTML elements
const startButton = document.getElementById("startRecording");
const transcriptDiv = document.getElementById("transcript");

// Initialize variables
let transcript = "";
let isRecording = false;

// Check if the browser supports SpeechRecognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) {
    alert("Your browser does not support speech recognition. Please try a different browser.");
} else {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;

    // Start/Stop recording with a single button
    startButton.addEventListener("click", () => {
        if (!isRecording) {
            // Start recording
            transcript = "";
            transcriptDiv.textContent = "Listening...";
            recognition.start();
            startButton.textContent = "Stop Recording";
            isRecording = true;
        } else {
            // Stop recording
            recognition.stop();
            startButton.textContent = "Start Recording";
            isRecording = false;
        }
    });

    // Handle speech recognition results
    recognition.addEventListener("result", (event) => {
        transcript = Array.from(event.results)
            .map((result) => result[0].transcript)
            .join("");
        transcriptDiv.textContent = `You said: "${transcript}"`;
    });

    // Handle errors
    recognition.addEventListener("error", (event) => {
        transcriptDiv.textContent = "Error: " + event.error;
        startButton.textContent = "Start Recording";
        isRecording = false;
    });

    // After processing transcript and receiving response from the backend
    recognition.addEventListener("end", () => {
        if (transcript) {
            // Send the transcript to the backend
            fetch("/process-transcript", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ transcript }),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log(`Received audio file: ${data.audio_file}`);
                    if (data.audio_generated) {
                        transcriptDiv.textContent = "";  // Clear any displayed text                    

                        // Set audio source dynamically to the generated audio file
                        const audioPlayer = document.getElementById("audioPlayer");
                        const audioSource = document.getElementById("audioSource");
                        audioSource.src = `/${data.audio_file}`;  // Use the exact filename returned from the backend
                        audioPlayer.style.display = "block";
                        audioPlayer.load();
                        audioPlayer.play();
                    } else {
                        transcriptDiv.textContent = "Error: Unable to process the transcript.";
                    }
                });
            startButton.textContent = "Start Recording";
            isRecording = false;
        }
    });
    }