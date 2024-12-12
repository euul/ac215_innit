import React from "react"
import PropTypes from "prop-types"
import MediaCard from "./MediaCard"

export default function MediaList({ title, items, type }) {
  return (
    <div className="mb-6">
      <h3 className="text-xl font-semibold text-green-500 mb-4">{title}</h3>
      <div className="space-y-4">
        {items.map((item, index) => (
          <MediaCard key={index} item={item} type={type} />
        ))}
      </div>
    </div>
  )
}

MediaList.propTypes = {
  title: PropTypes.string.isRequired,
  items: PropTypes.array.isRequired,
  type: PropTypes.oneOf(["article", "video"]).isRequired,
}
