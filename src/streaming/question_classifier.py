
# super simple for now...
def is_question(sentence):
    question_indicators = ['吗', '呢', '吧', '谁', '什么', '哪', '哪里', '为什么', '怎么', '?']
    for indicator in question_indicators:
        if indicator in sentence:
            return True
    return False