"""Flexible python implementation of the TextRank algoritm.

Based on paper "TextRank: Bringing Order into Texts" by Rada Mihalcea and Paul Tarau.
    https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf

All dependencies are optional and replaceable.

Functions:
    - extract_keywords
    - summarize
    - setup_nltk (if nltk is used)

Default dependencies:
    - tokenizer: str.split. `nltk_tokenizer` implementation is available as a better alternative (requires nltk).
    - filter: none. `filter_pos` nltk part of speech filter implementation is available as a better alternative (requires nltk).
    - graph engine: dict-based. `NetworkXGraphEngine` NetworkX implementation is available as a more feature-rich alternative (requires networkx).
    - distance: editdistance.eval (requires editdistance). spaCy semantic similarity might be a better alternative (requires spaCy).
"""

import itertools
from typing import Callable, Protocol

type DistanceFn = Callable[[str, str, str], float]  # str1, str2, lang -> float
type TokenizerFn = Callable[[str, str], list[str]]  # text, lang -> tokens
type FilterFn = Callable[[list[str], str], list[str]]  # tokens, lang -> filtered tokens

# Helper functions


def setup_nltk():
    """Download required resources."""
    import nltk

    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    print("Completed resource downloads.")


def nltk_tokenizer(text: str, lang: str) -> list[str]:
    """Tokenize text using NLTK."""
    import nltk

    lang_map = {
        "en": "english",
        "de": "german",
        "ru": "russian",
        "ua": "ukrainian",
        "fr": "french",
        "es": "spanish",
        "it": "italian",
        "pt": "portuguese",
        "nl": "dutch",
        "tr": "turkish",
        "sv": "swedish",
        "no": "norwegian",
        "fi": "finnish",
        "da": "danish",
        "pl": "polish",
        "cs": "czech",
        "ro": "romanian",
        "hu": "hungarian",
        "el": "greek",
        "bg": "bulgarian",
        "sl": "slovene",
        "hr": "croatian",
        "lt": "lithuanian",
        "lv": "latvian",
        "et": "estonian",
        "sk": "slovak",
        "sr": "serbian",
        "he": "hebrew",
        "ar": "arabic",
        "zh": "chinese",
        "ja": "japanese",
        "ko": "korean",
    }
    punkt_lang = lang_map.get(lang, "english")

    sent_detector = nltk.data.load(f"tokenizers/punkt/{punkt_lang}.pickle")
    sentence_tokens = sent_detector.tokenize(text.strip())
    return sentence_tokens  # nltk.word_tokenize(text)


def simple_tokenizer(text: str, lang: str) -> list[str]:
    """Simple tokenizer that splits text into words."""
    for char in [".", ",", ";", ":", "!", "?", "(", ")"]:
        text = text.replace(char, "")
    return text.split()


def filter_pos(word_tokens, lang: str, tags=["NN", "JJ", "NNP"]):
    """Apply syntactic filters based on POS tags."""
    import nltk

    tagged = nltk.pos_tag(word_tokens)
    return [item for item in tagged if item[1] in tags]


def no_filter(word_tokens: list[str], lang: str) -> list[str]:
    return word_tokens


def normalize(tagged: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Return a list of tuples with the first item's periods removed."""
    return [(item[0].replace(".", ""), item[1]) for item in tagged]


def unique_everseen(iterable: list[str], key: Callable[[str], str] | None = None) -> list[str]:
    """List unique elements in order of appearance.

    Examples:
        unique_everseen('AAAABBBCCDAABBB') --> A B C D
        unique_everseen('ABBCcAD', str.lower) --> A B C D
    """
    seen = set()
    seen_add = seen.add

    result = []
    for element in iterable:
        k = key(element) if key else element
        if k not in seen:
            seen_add(k)
            result.append(element)
    return result


def default_levenshtein(a: str, b: str, lang: str) -> float:
    import editdistance

    return editdistance.eval(a, b)


# GraphEngine abstraction


class GraphEngineProtocol(Protocol):
    def build(self, nodes: list[str], distance_fn: DistanceFn, lang: str): ...
    def pagerank(self) -> dict[str, float]: ...


class SimpleGraphEngine(GraphEngineProtocol):
    """Simple pure-Python GraphEngine implementation (unweighted PageRank)."""

    def __init__(self):
        self.graph: dict[str, dict[str, float]] = {}
        self.nodes: list[str] = []

    def build(self, nodes: list[str], distance_fn: DistanceFn, lang: str):
        self.nodes = nodes
        self.graph = {node: {} for node in nodes}
        for a, b in itertools.combinations(nodes, 2):
            w = distance_fn(a, b, lang)
            self.graph[a][b] = w
            self.graph[b][a] = w

    def pagerank(self) -> dict[str, float]:
        # Weighted PageRank (very basic, not optimized)
        ranks = {node: 1.0 for node in self.nodes}
        d = 0.85
        num_iter = 20
        N = len(self.nodes)
        for _ in range(num_iter):
            new_ranks = {}
            for node in self.nodes:
                rank_sum = 0.0
                for neighbor, weight in self.graph[node].items():
                    total_weight = sum(self.graph[neighbor].values())
                    if total_weight > 0:
                        rank_sum += ranks[neighbor] * (weight / total_weight)
                new_ranks[node] = (1 - d) / N + d * rank_sum
            ranks = new_ranks
        return ranks


class NetworkXGraphEngine(GraphEngineProtocol):
    """GraphEngine Implementation using NetworkX as a graph library"""

    def __init__(self):
        import networkx as nx

        self.nx = nx
        self.graph = None

    def build(self, nodes: list[str], distance_fn: DistanceFn, lang: str):
        self.graph = self.nx.Graph()
        self.graph.add_nodes_from(nodes)
        nodePairs = list(itertools.combinations(nodes, 2))
        for a, b in nodePairs:
            w = distance_fn(a, b, lang)
            self.graph.add_edge(a, b, weight=w)

    def pagerank(self) -> dict[str, float]:
        assert self.graph is not None, "Graph not built"
        return self.nx.pagerank(self.graph, weight="weight")


# TextRank Implementation


def extract_keywords(
    text: str,
    language: str = "en",
    tokenizer_fn: TokenizerFn = simple_tokenizer,
    filter_fn: FilterFn = filter_pos,
    distance_fn: DistanceFn = default_levenshtein,
    graph_engine: GraphEngineProtocol | None = None,
) -> set[str]:
    """
    Return a set of key phrases.

    Parameters
    ----------
    text : str
        Input text to extract key phrases from.
    language : str, optional
        ISO 639-1 code for language (default: 'en').
    tokenizer_fn : TokenizerFn
        Function to tokenize text (default: str.split). nltk_tokenizer is available as a better alternative.
    filter_fn : FilterFn
        Function to filter key tokens, for example, by part-of-speech (default: none). filter_pos is available as a better alternative.
    distance_fn : DistanceFn
        Function to compute distance between two words (default: Levenshtein). spaCy semantic similarity might be a better alternative.
    graph_engine : GraphEngineProtocol | None
        Graph engine instance to use (default: SimpleGraphEngine). NetworkXGraphEngine option is available as a better alternative.

    Returns
    -------
    set[str]
        Set of extracted key phrases.
    """
    graph_engine = graph_engine or SimpleGraphEngine()

    word_tokens = tokenizer_fn(text, language)
    textlist = [x[0] for x in word_tokens]

    word_tokens = filter_fn(word_tokens, language)
    word_tokens = normalize(word_tokens)

    unique_word_set = unique_everseen([x[0] for x in word_tokens])
    word_set_list = list(unique_word_set)

    graph_engine.build(word_set_list, distance_fn, language)
    calculated_page_rank = graph_engine.pagerank()

    keyphrases = sorted(calculated_page_rank, key=lambda k: calculated_page_rank[k], reverse=True)

    one_third = len(word_set_list) // 3
    keyphrases = keyphrases[0 : one_third + 1]

    modified_key_phrases: set[str] = set()

    i = 0
    while i < len(textlist):
        w = textlist[i]
        if w in keyphrases:
            phrase_ws = [w]
            i += 1
            while i < len(textlist) and textlist[i] in keyphrases:
                phrase_ws.append(textlist[i])
                i += 1

            phrase = " ".join(phrase_ws)
            if phrase not in modified_key_phrases:
                modified_key_phrases.add(phrase)
        else:
            i += 1

    return modified_key_phrases


def summarize(
    text: str,
    summary_length_words: int = 100,
    clean_sentences: bool = False,
    language: str = "en",
    tokenizer_fn: TokenizerFn = simple_tokenizer,
    distance_fn: DistanceFn = default_levenshtein,
    graph_engine: GraphEngineProtocol | None = None,
) -> str:
    """
    Return a paragraph formatted summary of the source text.

    Parameters
    ----------
    text : str
        Input text to summarize.
    summary_length_words : int, optional
        Maximum number of words in the summary (default: 100).
    clean_sentences : bool, optional
        If True, truncate summary at last sentence-ending period (default: False).
    language : str, optional
        ISO 639-1 code for language (default: 'en').
    tokenizer_fn : TokenizerFn
        Function to tokenize text (default: str.split). nltk_tokenizer is available as a better alternative.
    distance_fn : DistanceFn
        Function to compute distance between two words (default: Levenshtein). spaCy semantic similarity might be a better alternative.
    graph_engine : GraphEngineProtocol | None
        Graph engine instance to use (default: SimpleGraphEngine). NetworkXGraphEngine option is available as a better alternative.

    Returns
    -------
    str
        The extracted summary as a string.
    """

    graph_engine = graph_engine or SimpleGraphEngine()
    sentence_tokens = tokenizer_fn(text, language)
    graph_engine.build(sentence_tokens, distance_fn, language)
    calculated_page_rank = graph_engine.pagerank()

    sentences = sorted(calculated_page_rank, key=lambda k: calculated_page_rank[k], reverse=True)

    summary = " ".join(sentences)
    summary_words = summary.split()
    summary_words = summary_words[0:summary_length_words]
    dot_indices = [idx for idx, word in enumerate(summary_words) if word.find(".") != -1]
    if clean_sentences and dot_indices:
        last_dot = max(dot_indices) + 1
        summary = " ".join(summary_words[0:last_dot])
    else:
        summary = " ".join(summary_words)

    return summary
