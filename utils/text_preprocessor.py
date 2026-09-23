import spacy

nlp = spacy.load("en_core_web_sm")


def preprocess_text(text):
    """
    Clean and lemmatize resume/JD text using spaCy.
    """
    doc = nlp(text)

    tokens = []

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue

        if token.like_email:
            continue

        tokens.append(token.lemma_.lower())

    return " ".join(tokens)