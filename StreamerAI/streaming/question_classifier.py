class QuestionDetector:
    """A class for detecting whether a sentence is a question."""

    @staticmethod
    def is_question(sentence):
        """Detect whether the given sentence is a question.

        Args:
            sentence (str): the sentence to analyze

        Returns:
            bool: True if the sentence is a question, False otherwise
        """
        question_indicators = ['吗', '呢', '吧', '谁', '什么', '哪', '哪里', '为什么', '怎么', '?']
        for indicator in question_indicators:
            if indicator in sentence:
                return True
        return False