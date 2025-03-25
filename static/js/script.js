document.addEventListener("DOMContentLoaded", () => {
  // Mobile menu toggle
  const mobileMenu = document.getElementById("mobile-menu")
  const navMenu = document.querySelector(".nav-menu")

  if (mobileMenu) {
    mobileMenu.addEventListener("click", () => {
      mobileMenu.classList.toggle("active")
      navMenu.classList.toggle("active")

      // Toggle menu icon
      const bars = mobileMenu.querySelectorAll(".bar")
      if (navMenu.classList.contains("active")) {
        bars[0].style.transform = "rotate(-45deg) translate(-5px, 6px)"
        bars[1].style.opacity = "0"
        bars[2].style.transform = "rotate(45deg) translate(-5px, -6px)"
      } else {
        bars[0].style.transform = "none"
        bars[1].style.opacity = "1"
        bars[2].style.transform = "none"
      }
    })
  }

  // Text-to-Speech functionality
  const voiceSelect = document.getElementById("voice-select")
  const textInput = document.getElementById("text-input")
  const generateBtn = document.getElementById("generate-btn")
  const clearBtn = document.getElementById("clear-btn")
  const audioContainer = document.getElementById("audio-container")
  const audioPlayer = document.getElementById("audio-player")
  const downloadBtn = document.getElementById("download-btn")
  const loadingIndicator = document.getElementById("loading-indicator")
  const stabilitySlider = document.getElementById("stability")
  const claritySlider = document.getElementById("clarity")
  const stabilityValue = document.getElementById("stability-value")
  const clarityValue = document.getElementById("clarity-value")

  // Current audio URL for download
  let currentAudioUrl = ""
  let currentAudioBlob = null

  // Initialize sliders if they exist
  if (stabilitySlider && stabilityValue) {
    stabilitySlider.addEventListener("input", function () {
      stabilityValue.textContent = this.value
    })
  }

  if (claritySlider && clarityValue) {
    claritySlider.addEventListener("input", function () {
      clarityValue.textContent = this.value
    })
  }

  // Fetch available voices if on the main page
  if (voiceSelect) {
    fetchVoices()

    // Event Listeners
    generateBtn.addEventListener("click", generateSpeech)
    clearBtn.addEventListener("click", clearText)

    if (downloadBtn) {
      downloadBtn.addEventListener("click", downloadAudio)
    }
  }

  // Functions
  async function fetchVoices() {
    try {
      const response = await fetch("/get_voices")
      const data = await response.json()

      if (data.voices && data.voices.length > 0) {
        // Clear loading option
        voiceSelect.innerHTML = ""

        // Add voices to select
        data.voices.forEach((voice) => {
          const option = document.createElement("option")
          option.value = voice.voice_id
          option.textContent = voice.name
          voiceSelect.appendChild(option)
        })
      } else {
        voiceSelect.innerHTML = '<option value="">No voices available</option>'
      }
    } catch (error) {
      console.error("Error fetching voices:", error)
      voiceSelect.innerHTML = '<option value="">Error loading voices</option>'
    }
  }

  async function generateSpeech() {
    const text = textInput.value.trim()
    const voiceId = voiceSelect.value

    if (!text) {
      showNotification("Please enter some text", "error")
      return
    }

    if (voiceId === "loading" || voiceId === "") {
      showNotification("Please select a voice", "error")
      return
    }

    // Get stability and clarity values if available
    const stability = stabilitySlider ? Number.parseFloat(stabilitySlider.value) : 0.5
    const clarity = claritySlider ? Number.parseFloat(claritySlider.value) : 0.5

    // Show loading indicator
    loadingIndicator.style.display = "flex"
    generateBtn.disabled = true

    try {
      // First try the server API
      const response = await fetch("/text_to_speech", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text,
          voice_id: voiceId,
          stability: stability,
          clarity: clarity,
        }),
      })

      const data = await response.json()

      if (data.success) {
        // If we're in demo mode and the server returned a demo file URL
        if (data.demo_mode) {
          // Use Web Speech API as a fallback
          generateSpeechWithWebAPI(text, voiceId)
          return
        }

        // Hide loading indicator
        loadingIndicator.style.display = "none"
        generateBtn.disabled = false

        // Set audio source and show player
        audioPlayer.src = data.file_url
        audioContainer.style.display = "block"

        // Store URL for download
        currentAudioUrl = data.file_url

        // Scroll to audio player
        audioContainer.scrollIntoView({ behavior: "smooth" })

        // Play audio
        audioPlayer.play()
      } else {
        throw new Error(data.error || "Failed to generate speech")
      }
    } catch (error) {
      console.error("Error generating speech:", error)

      // Fallback to Web Speech API
      generateSpeechWithWebAPI(text, voiceId)
    }
  }

  function generateSpeechWithWebAPI(text, voiceId) {
    // Check if browser supports speech synthesis
    if ("speechSynthesis" in window) {
      // Create a new SpeechSynthesisUtterance instance
      const utterance = new SpeechSynthesisUtterance(text)

      // Get available voices
      let voices = window.speechSynthesis.getVoices()

      // If voices aren't loaded yet, wait for them
      if (voices.length === 0) {
        window.speechSynthesis.onvoiceschanged = () => {
          voices = window.speechSynthesis.getVoices()
          setVoiceAndSpeak()
        }
      } else {
        setVoiceAndSpeak()
      }

      function setVoiceAndSpeak() {
        // Map the mock voice ID to a voice type
        let voiceIndex = 0

        switch (voiceId) {
          case "mock_voice_1": // Male
            // Find a male voice
            for (let i = 0; i < voices.length; i++) {
              if (voices[i].name.toLowerCase().includes("male")) {
                voiceIndex = i
                break
              }
            }
            break
          case "mock_voice_2": // Female
            // Find a female voice
            for (let i = 0; i < voices.length; i++) {
              if (voices[i].name.toLowerCase().includes("female")) {
                voiceIndex = i
                break
              }
            }
            break
          case "mock_voice_4": // Child
            // Try to find a higher pitched voice
            utterance.pitch = 1.5
            utterance.rate = 1.1
            break
          case "mock_voice_5": // Elder
            // Try to find a slower, deeper voice
            utterance.pitch = 0.8
            utterance.rate = 0.8
            break
          default:
            // Use default voice
            break
        }

        // Set the voice
        if (voices.length > voiceIndex) {
          utterance.voice = voices[voiceIndex]
        }

        // Create a MediaRecorder to capture the audio
        const audioChunks = []
        const audioContext = new (window.AudioContext || window.webkitAudioContext)()
        const destination = audioContext.createMediaStreamDestination()
        const mediaRecorder = new MediaRecorder(destination.stream)

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            audioChunks.push(e.data)
          }
        }

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/mp3" })
          const audioUrl = URL.createObjectURL(audioBlob)

          // Hide loading indicator
          loadingIndicator.style.display = "none"
          generateBtn.disabled = false

          // Set audio source and show player
          audioPlayer.src = audioUrl
          audioContainer.style.display = "block"

          // Store blob and URL for download
          currentAudioBlob = audioBlob
          currentAudioUrl = audioUrl

          // Scroll to audio player
          audioContainer.scrollIntoView({ behavior: "smooth" })

          // Play audio
          audioPlayer.play()
        }

        // Start recording
        mediaRecorder.start()

        // Speak the text
        window.speechSynthesis.speak(utterance)

        // When speech is done, stop recording
        utterance.onend = () => {
          mediaRecorder.stop()
        }

        // Fallback in case onend doesn't fire
        setTimeout(() => {
          if (mediaRecorder.state === "recording") {
            mediaRecorder.stop()
          }
        }, text.length * 100) // Rough estimate of speech duration
      }
    } else {
      // Browser doesn't support speech synthesis
      showNotification("Your browser does not support text-to-speech", "error")
      loadingIndicator.style.display = "none"
      generateBtn.disabled = false
    }
  }

  function clearText() {
    textInput.value = ""
    textInput.focus()
  }

  function downloadAudio() {
    if (currentAudioBlob) {
      // If we have a blob (from Web Speech API), use that
      const link = document.createElement("a")
      link.href = currentAudioUrl
      link.download = "speech_" + Date.now() + ".mp3"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } else if (currentAudioUrl) {
      // Otherwise use the URL from the server
      const link = document.createElement("a")
      link.href = currentAudioUrl
      link.download = "speech_" + Date.now() + ".mp3"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  function showNotification(message, type = "info") {
    // Create a custom notification
    const notification = document.createElement("div")
    notification.className = `notification ${type}`
    notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === "error" ? "fa-exclamation-circle" : "fa-info-circle"}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `

    document.body.appendChild(notification)

    // Add styles
    notification.style.position = "fixed"
    notification.style.bottom = "20px"
    notification.style.right = "20px"
    notification.style.backgroundColor = type === "error" ? "#fee2e2" : "#e0f2fe"
    notification.style.color = type === "error" ? "#ef4444" : "#0ea5e9"
    notification.style.padding = "1rem"
    notification.style.borderRadius = "0.5rem"
    notification.style.boxShadow = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    notification.style.display = "flex"
    notification.style.alignItems = "center"
    notification.style.justifyContent = "space-between"
    notification.style.zIndex = "1000"
    notification.style.maxWidth = "300px"
    notification.style.animation = "slideIn 0.3s ease-out forwards"

    // Add keyframes for animation
    const style = document.createElement("style")
    style.innerHTML = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `
    document.head.appendChild(style)

    // Close button functionality
    const closeBtn = notification.querySelector(".notification-close")
    closeBtn.addEventListener("click", () => {
      notification.style.animation = "slideOut 0.3s ease-out forwards"
      setTimeout(() => {
        document.body.removeChild(notification)
      }, 300)
    })

    // Auto close after 5 seconds
    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.style.animation = "slideOut 0.3s ease-out forwards"
        setTimeout(() => {
          if (document.body.contains(notification)) {
            document.body.removeChild(notification)
          }
        }, 300)
      }
    }, 5000)
  }

  // Add example text if on main page
  if (textInput && textInput.value === "") {
    textInput.value = "Welcome to VoiceGenius! Type or paste your text here and click Generate Speech to hear it."
    if (document.getElementById("char-count")) {
      document.getElementById("char-count").textContent = textInput.value.length + " characters"
    }
  }
})

