from utils.logger import get_logger

logger = get_logger(__name__)

# Common English words for basic prediction
WORD_LIST = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know",
    "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come",
    "its", "over", "think", "also", "back", "after", "use", "two", "how",
    "our", "work", "first", "well", "way", "even", "new", "want", "because",
    "any", "these", "give", "day", "most", "us", "great", "between", "need",
    "large", "often", "hand", "high", "place", "hold", "turn", "help", "home",
    "hello", "here", "have", "happy", "hard", "hate", "head", "hear",
    "please", "python", "program", "project", "person", "play", "point",
    "water", "world", "write", "where", "while", "which", "white", "wrong",
    "should", "still", "start", "stop", "story", "study", "small", "smile",
    "thanks", "think", "thing", "those", "three", "through", "today",
    "together", "tomorrow", "tonight", "toward", "try", "turn", "type",
]


class WordPredictor:
    def __init__(self, max_suggestions: int = 3):
        self.max_suggestions = max_suggestions
        self.word_set        = sorted(set(WORD_LIST))
        logger.info("WordPredictor initialized.")

    def predict(self, partial: str) -> list[str]:
        """Return up to max_suggestions words starting with partial."""
        if not partial or partial.isspace():
            return []

        partial = partial.lower().split()[-1]  # last word being typed

        if not partial:
            return []

        matches = [w for w in self.word_set if w.startswith(partial)]
        return matches[:self.max_suggestions]