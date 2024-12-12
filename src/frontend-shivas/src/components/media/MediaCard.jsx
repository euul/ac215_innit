import React from "react"
import { useRouter } from "next/navigation"
import PropTypes from "prop-types"

export default function MediaCard({ item, type }) {
  const router = useRouter()

  const handleClick = () => {
    if (type === "article" && item.id) {
      router.push(`/media/articles/${item.id}`)
    } else if (type === "video" && item.video_id) {
      router.push(`/media/videos/${item.video_id}`)
    } else {
      console.error(`ID not found for ${type}:`, item)
    }
  }

  return (
    <div
      onClick={handleClick}
      className={`cursor-pointer rounded-lg shadow-md transform transition-transform hover:scale-105 border border-green-600 ${
        type === "article"
          ? "bg-gradient-to-r from-black-600 to-black-600"
          : "bg-gradient-to-r from-black-600 to-black-600"
      }`}
    >
      <div className="p-4 text-white">
        <h3 className="text-lg font-semibold text-white">
          {type === "article" ? item.Title : item.video_name}
        </h3>
      </div>
    </div>
  )
}

MediaCard.propTypes = {
  item: PropTypes.object.isRequired,
  type: PropTypes.oneOf(["article", "video"]).isRequired,
}
