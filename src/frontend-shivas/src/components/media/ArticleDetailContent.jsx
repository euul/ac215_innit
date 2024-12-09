import React from "react"
import PropTypes from "prop-types"

export default function ArticleDetailContent({ article }) {
  if (!article) {
    return (
      <div className="text-center mt-12">
        <h2 className="text-gray-700 text-2xl">Article not found</h2>
      </div>
    )
  }

  return (
    <article className="flex flex-col items-center px-4 pb-40 mt-12">
      {/* Title */}
      <header>
        <h2 className="text-3xl font-bold text-blue-600 text-center mb-6">
          {article.Title || "Untitled Article"}
        </h2>
      </header>

      {/* Key Words Section */}
      {article.vocab && (
        <section className="w-full max-w-3xl text-left mb-8">
          <h3 className="text-xl text-green-500 mb-4">Key Words:</h3>
          <ul className="list-disc pl-8 text-green-500">
            {article.vocab.split("\n").map((word, index) => (
              <li key={index} className="mb-2">
                {word}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Scrollable Text */}
      {article.Text ? (
        <section className="max-h-96 overflow-y-auto w-full max-w-3xl p-6 bg-gray-100 rounded-lg shadow-md">
          {article.Text.split("\n").map((paragraph, index) => (
            <p
              key={index}
              className="mb-6 text-gray-700 text-lg leading-relaxed text-justify"
            >
              {paragraph}
            </p>
          ))}
        </section>
      ) : (
        <p className="text-gray-500 text-lg mt-4">No content available.</p>
      )}
    </article>
  )
}

ArticleDetailContent.propTypes = {
  article: PropTypes.shape({
    Title: PropTypes.string.isRequired,
    vocab: PropTypes.string,
    Text: PropTypes.string.isRequired,
  }),
}
