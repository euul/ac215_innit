import React, { useEffect, useRef } from "react"

function MediaPlayer({ videoId, onTimeUpdate }) {
  const playerRef = useRef(null)
  const playerInstance = useRef(null)

  useEffect(() => {
    let interval

    const initializePlayer = () => {
      if (window.YT && window.YT.Player) {
        playerInstance.current = new window.YT.Player(playerRef.current, {
          videoId: videoId.split("&")[0], // Clean videoId here
          events: {
            onReady: onPlayerReady,
            onStateChange: onPlayerStateChange,
          },
          playerVars: {
            autoplay: 1, // Attempt autoplay
            rel: 0, // Disable related videos at the end
            modestbranding: 1, // Reduce YouTube branding
          },
        })
      } else {
        console.error("YouTube Player API not available")
      }
    }

    const onPlayerReady = () => {
      console.log("YouTube Player is ready")
      playerInstance.current.playVideo() // Attempt to play the video immediately
    }

    const onPlayerStateChange = (event) => {
      if (event.data === window.YT.PlayerState.PLAYING) {
        interval = setInterval(() => {
          const currentTime = playerInstance.current?.getCurrentTime()
          if (currentTime && onTimeUpdate) {
            onTimeUpdate(currentTime)
          }
        }, 500) // Check every 500ms
      } else {
        clearInterval(interval)
      }
    }

    const loadYouTubeAPI = () => {
      if (!window.YT || !window.YT.Player) {
        const script = document.createElement("script")
        script.src = "https://www.youtube.com/iframe_api"
        script.async = true
        document.body.appendChild(script)
      }

      window.onYouTubeIframeAPIReady = () => {
        initializePlayer()
      }
    }

    loadYouTubeAPI()

    return () => {
      clearInterval(interval)
      if (playerInstance.current) {
        playerInstance.current.destroy()
      }
    }
  }, [videoId, onTimeUpdate])

  return (
    <div style={{ textAlign: "center", marginTop: "2rem" }}>
      <div ref={playerRef} style={{ width: "100%", height: "315px" }} />
    </div>
  )
}

export default MediaPlayer
