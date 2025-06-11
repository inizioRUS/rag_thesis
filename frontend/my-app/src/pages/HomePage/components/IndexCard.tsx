import { useState } from "react";
import { Link } from "react-router-dom";

interface Index {
  id: string;
  name: string;
  description: string;
  rating: number;
  averageRating: number;
  countRating: number
}

const IndexCard = ({ index }: { index: Index }) => {
  const [hoverRating, setHoverRating] = useState(0);
  const [currentRating, setCurrentRating] = useState(index.rating);

  return (
    <div className="card">
      <h3 className="card-title">{index.name}</h3>
      <p className="card-description">{index.description}</p>

      <div className="rating">
        <div className="stars">
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={star}
              className={`star ${star <= (hoverRating || currentRating) ? 'filled' : ''}`}
              onMouseEnter={() => setHoverRating(star)}
              onMouseLeave={() => setHoverRating(0)}
              onClick={() => setCurrentRating(star)}
            >
              ★
            </span>
          ))}
        </div>
        <span className="rating-text">Ваш рейтинг: {currentRating}/5</span>
      </div>

      <div className="average-rating">
        <div className="stars static-stars">
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={`avg-${star}`}
              className={`star ${star <= index.averageRating ? 'filled' : ''}`}
            >
              ★
            </span>
          ))}
        </div>
        <span className="rating-text">
          Общий рейтинг: {index.averageRating}/5 ({index.countRating} оценок)
        </span>
      </div>

      <a href={`/index/${index.id}`} className="card-link">Перейти в чат</a>
    </div>
  );
};

export default IndexCard;
