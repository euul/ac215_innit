import React, { useEffect, useRef, useState } from "react"

function MediaPlayer({ videoId, onTimeUpdate }) {
  const playerRef = useRef(null)
  const playerInstance = useRef(null)
  const [isApiLoaded, setIsApiLoaded] = useState(false)

  const initializePlayer = () => {
    if (window.YT && window.YT.Player) {
      playerInstance.current = new window.YT.Player(playerRef.current, {
        videoId: videoId.split("&")[0], // Clean videoId
        events: {
          onReady: onPlayerReady,
          onStateChange: onPlayerStateChange,
        },
        playerVars: {
          autoplay: 0, // Prevent autoplay
          rel: 0,
          modestbranding: 1,
        },
      })
    } else {
      console.error("YouTube Player API is not available")
    }
  }

  const onPlayerReady = () => {
    console.log("YouTube Player is ready")
    // No `playVideo()` here; the user needs to start the video manually
  }

  const onPlayerStateChange = (event) => {
    if (event.data === window.YT.PlayerState.PLAYING) {
      const interval = setInterval(() => {
        const currentTime = playerInstance.current?.getCurrentTime()
        if (currentTime && onTimeUpdate) {
          onTimeUpdate(currentTime)
        }
      }, 500)
      playerInstance.current._interval = interval // Store the interval for cleanup
    } else if (event.data === window.YT.PlayerState.ENDED) {
      clearInterval(playerInstance.current._interval)
    }
  }

  const loadYouTubeAPI = () => {
    if (!window.YT || !window.YT.Player) {
      const script = document.createElement("script")
      script.src = "https://www.youtube.com/iframe_api"
      script.async = true
      script.onload = () => setIsApiLoaded(true) // Mark API as loaded
      document.body.appendChild(script)
    } else {
      setIsApiLoaded(true) // API is already loaded
    }
  }

  useEffect(() => {
    loadYouTubeAPI()

    return () => {
      if (playerInstance.current) {
        clearInterval(playerInstance.current._interval) // Clear interval on cleanup
        playerInstance.current.destroy()
      }
    }
  }, [])

  useEffect(() => {
    if (isApiLoaded) {
      initializePlayer()
    }
  }, [isApiLoaded, videoId])

  return (
    <div style={{ textAlign: "center", marginTop: "2rem" }}>
      <div ref={playerRef} style={{ width: "100%", height: "315px" }} />
    </div>
  )
}

export default MediaPlayer
