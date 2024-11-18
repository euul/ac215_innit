import React, { useEffect, useRef } from "react"

function MediaPlayer({ videoId, onTimeUpdate }) {
  const playerRef = useRef(null) // Reference to the player container
  const ytPlayer = useRef(null) // Reference to the YouTube player instance

  const loadYouTubeAPI = () => {
    return new Promise((resolve) => {
      if (window.YT && window.YT.Player) {
        resolve()
      } else {
        const tag = document.createElement("script")
        tag.src = "https://www.youtube.com/iframe_api"
        const firstScriptTag = document.getElementsByTagName("script")[0]
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag)

        window.onYouTubeIframeAPIReady = () => {
          resolve()
        }
      }
    })
  }

  const initializePlayer = async () => {
    await loadYouTubeAPI()

    if (playerRef.current && videoId) {
      if (ytPlayer.current) {
        ytPlayer.current.destroy()
      }

      ytPlayer.current = new window.YT.Player(playerRef.current, {
        videoId: cleanVideoId(videoId),
        playerVars: {
          autoplay: 0,
          controls: 1,
          rel: 0,
        },
        events: {
          onReady: () => {
            console.log("YouTube Player is ready")
          },
          onStateChange: (event) => {
            if (event.data === window.YT.PlayerState.PLAYING) {
              startTrackingTime()
            }
          },
        },
      })
    }
  }

  const cleanVideoId = (id) => {
    return id.split("&")[0]
  }

  const startTrackingTime = () => {
    const interval = setInterval(() => {
      if (
        ytPlayer.current &&
        ytPlayer.current.getPlayerState() === window.YT.PlayerState.PLAYING
      ) {
        const currentTime = ytPlayer.current.getCurrentTime()
        if (onTimeUpdate) {
          onTimeUpdate(currentTime)
        }
      } else {
        clearInterval(interval)
      }
    }, 500)
  }

  useEffect(() => {
    initializePlayer()
  }, [videoId])

  return (
    <div style={{ textAlign: "center", marginTop: "2rem" }}>
      {videoId ? (
        <div
          ref={playerRef}
          style={{
            width: "100%",
            height: "315px",
          }}
        ></div>
      ) : (
        <p>Select a video to display.</p>
      )}
    </div>
  )
}

export default MediaPlayer
