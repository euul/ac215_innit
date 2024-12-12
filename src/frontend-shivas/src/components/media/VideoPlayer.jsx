import React, { useEffect, useRef } from "react"
import PropTypes from "prop-types"
import styles from "./VideoPlayer.module.css" // Import CSS module

// Utility function to clean the video ID
const cleanVideoId = (id) => id.split("&")[0] // Removes query parameters if present

export default function VideoPlayer({ videoId, onTimeUpdate }) {
  const playerRef = useRef(null)
  const ytPlayer = useRef(null)

  const loadYouTubeAPI = () => {
    return new Promise((resolve) => {
      if (window.YT && window.YT.Player) {
        resolve()
      } else {
        const tag = document.createElement("script")
        tag.src = "https://www.youtube.com/iframe_api"
        const firstScriptTag = document.getElementsByTagName("script")[0]
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag)

        window.onYouTubeIframeAPIReady = () => resolve()
      }
    })
  }

  const initializePlayer = async () => {
    await loadYouTubeAPI()

    if (playerRef.current && videoId) {
      if (ytPlayer.current) {
        ytPlayer.current.destroy()
      }

      console.log(
        "Initializing YouTube Player with video ID:",
        cleanVideoId(videoId)
      ) // Debugging log

      ytPlayer.current = new window.YT.Player(playerRef.current, {
        videoId: cleanVideoId(videoId), // Use cleaned video ID
        playerVars: {
          autoplay: 0,
          controls: 1,
          rel: 0,
          origin: window.location.origin, // Dynamically set the origin to match the current frontend
        },
        events: {
          onStateChange: (event) => {
            if (event.data === window.YT.PlayerState.PLAYING) {
              startTrackingTime()
            }
          },
        },
      })
    }
  }

  const startTrackingTime = () => {
    const interval = setInterval(() => {
      if (
        ytPlayer.current &&
        ytPlayer.current.getPlayerState() === window.YT.PlayerState.PLAYING
      ) {
        const currentTime = ytPlayer.current.getCurrentTime()
        onTimeUpdate?.(currentTime)
      } else {
        clearInterval(interval)
      }
    }, 500)
  }

  useEffect(() => {
    initializePlayer()
  }, [videoId])

  return (
    <div className={styles.videoContainer}>
      {videoId ? (
        <div ref={playerRef} className={styles.videoPlayer}></div>
      ) : (
        <p className={styles.noVideo}>No video selected.</p>
      )}
    </div>
  )
}

VideoPlayer.propTypes = {
  videoId: PropTypes.string.isRequired,
  onTimeUpdate: PropTypes.func,
}
