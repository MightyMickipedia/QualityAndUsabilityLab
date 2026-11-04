# perturb.py
# rule-based perturbation script for the LLM-as-a-Judge robustness study
#
# takes the three input jsonl files, introduces errors at target score levels 1-5,
# and writes the perturbed summaries back out in the same format.
#
# quick start:
#   python perturb.py --input_faith adv_proj_faithfulness.jsonl \
#                     --input_nrd   adv_proj_nrd.jsonl \
#                     --input_gram  adv_proj_grammaticality.jsonl
#
# run with --test to check the subclause regex against a few hardcoded sentences.
# change SCORE_DISTRIBUTION below if you want a different split.

import json, re, random, argparse

import spacy
import numpy as np
import pandas as pd


# tweak this if you want a different score split
SCORE_DISTRIBUTION = {
    5: 0.20,
    4: 0.20,
    3: 0.20,
    2: 0.20,
    1: 0.20,
}
RANDOM_SEED = 42


# entity lists used for swapping names, places, orgs

GERMAN_CITIES = [
    "Berlin","München","Hamburg","Köln","Frankfurt","Stuttgart","Düsseldorf",
    "Leipzig","Dortmund","Essen","Bremen","Dresden","Hannover","Nürnberg",
    "Duisburg","Bochum","Wuppertal","Bielefeld","Bonn","Münster","Karlsruhe",
    "Mannheim","Augsburg","Wiesbaden","Gelsenkirchen","Braunschweig","Kiel",
    "Chemnitz","Aachen","Halle","Magdeburg","Freiburg","Krefeld","Lübeck",
    "Erfurt","Mainz","Rostock","Kassel","Wien","Graz","Linz","Salzburg",
    "Innsbruck","Zürich","Basel","Bern","Genf","Lausanne",
]
GERMAN_ORGS = [
    "Bundesregierung","Bundestag","Bundesrat","Europäische Union",
    "Deutsche Bank","Volkswagen","BMW","Mercedes-Benz","Siemens",
    "Bosch","BASF","Bayer","Allianz","Deutsche Telekom","SAP",
    "Bundeswehr","SPD","CDU","CSU","FDP","Grüne","AfD",
    "ARD","ZDF","Spiegel","Zeit","FAZ","Süddeutsche Zeitung",
    "Weltgesundheitsorganisation","Vereinte Nationen","NATO","OECD",
]
GERMAN_COUNTRIES = [
    "Deutschland","Österreich","Schweiz","Frankreich","Italien","Spanien",
    "Polen","Niederlande","Belgien","Schweden","Norwegen","Dänemark",
    "Finnland","Portugal","Griechenland","Tschechien","Ungarn",
    "USA","China","Russland","Japan","Brasilien","Indien",
    "Großbritannien","Kanada","Australien","Südkorea","Türkei",
]


# spacy setup — blank German model, just need the sentencizer

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

nlp = spacy.blank("de")
nlp.add_pipe("sentencizer")


def fix_encoding(text: str) -> str:
    # some summaries in the dataset have encoding issues; only fix if we see the telltale chars
    sample = text[:50]
    if not any(0xC0 <= ord(c) <= 0xFF for c in sample):
        return text
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


def tokenize_sentences(text: str) -> list:
    doc = nlp(text)
    return [s.text.strip() for s in doc.sents if s.text.strip()]


# quite a few summaries start with "Hier ist der Artikel:" or similar — strip before perturbing
_RE_BOILERPLATE = re.compile(r"^(?:Hier ist [\w ]+:|\S[^\n]{0,80}[:\-])\s*\n?", re.IGNORECASE)

def _split_boilerplate(text: str):
    m = _RE_BOILERPLATE.match(text)
    if m:
        return text[:m.end()], text[m.end():]
    return "", text


# compiled regexes for numbers and named entities

_RE_YEAR      = re.compile(r'\b(1[89]\d{2}|20[0-2]\d)\b')
_RE_DECIMAL   = re.compile(r'\b(\d+)[.,](\d+)\b')
_RE_INTEGER   = re.compile(r'(?<![0-9])([2-9]\d{1,2})(?![0-9])')  # 2-999 range, deliberately skips year-like numbers
_RE_PERCENT   = re.compile(r'\b(\d+[.,]?\d*)\s*(%|Prozent)\b')
_RE_LARGE_NUM = re.compile(r'\b(\d+[.,]?\d*)\s*(Millionen|Milliarden|Tausend)\b')

_RE_CITY    = re.compile(r'\b(' + '|'.join(re.escape(c) for c in GERMAN_CITIES) + r')\b')
_RE_COUNTRY = re.compile(r'\b(' + '|'.join(re.escape(c) for c in GERMAN_COUNTRIES) + r')\b')
_RE_ORG     = re.compile(r'\b(' + '|'.join(re.escape(o) for o in GERMAN_ORGS) + r')\b')

_RE_ORPHAN_PRONOUN = re.compile(r'^(Er|Sie|Es|Dies)\b')

# im/am/etc. need to be expanded before we can swap articles
_CONTRACTIONS = {
    "im": "in dem", "ins": "in das", "am": "an dem",
    "zur": "zu der", "zum": "zu dem", "beim": "bei dem",
    "ans": "an das", "vom": "von dem", "ums": "um das",
}
_RE_CONTRACTION = re.compile(
    r'\b(' + '|'.join(re.escape(k) for k in _CONTRACTIONS) + r')\b'
)


# small helpers used all over the place

def _nz_int(lo: int, hi: int) -> int:
    choices = [x for x in range(lo, hi + 1) if x != 0]
    return random.choice(choices) if choices else (lo if lo != 0 else hi)


def _nz_float(lo: float, hi: float) -> float:
    val = random.uniform(lo, hi)
    return val if abs(val - 1.0) > 0.05 else hi


# numeric perturbation functions — each touches one number type

def _perturb_year(text: str, lo: int, hi: int) -> str:
    def sub(m):
        return str(int(m.group(1)) + _nz_int(lo, hi))
    return _RE_YEAR.sub(sub, text, count=1)


def _perturb_decimal(text: str, lo: float, hi: float) -> str:
    def sub(m):
        val = float(m.group(1) + "." + m.group(2))
        new = round(val * _nz_float(lo, hi), 1)
        return str(new).replace(".", ",")
    return _RE_DECIMAL.sub(sub, text, count=1)


def _perturb_integer(text: str, pct: float) -> str:
    def sub(m):
        val = int(m.group(1))
        delta = max(1, int(abs(val) * pct))
        return str(val + random.choice([-1, 1]) * delta)
    return _RE_INTEGER.sub(sub, text, count=1)


def _perturb_percent(text: str, lo: float, hi: float) -> str:
    def sub(m):
        val = float(m.group(1).replace(",", "."))
        delta = abs(random.uniform(lo, hi))
        new = max(0.1, val + random.choice([-1, 1]) * delta)
        return f"{new:.1f} {m.group(2)}".replace(".", ",")
    return _RE_PERCENT.sub(sub, text, count=1)


def _perturb_large_num(text: str, lo: float, hi: float) -> str:
    def sub(m):
        val = float(m.group(1).replace(",", "."))
        new = round(val * _nz_float(lo, hi), 1)
        return str(new).replace(".", ",") + " " + m.group(2)
    return _RE_LARGE_NUM.sub(sub, text, count=1)


# entity swap — replaces a matched entity with a random different one from the same pool

def _swap_from_list(text: str, pattern: re.Pattern, pool: list, n: int = 1) -> str:
    matches = list(pattern.finditer(text))
    if not matches:
        return text
    offset = 0
    for m in random.sample(matches, min(n, len(matches))):
        orig = m.group(1)
        repl = random.choice([x for x in pool if x != orig] or pool)
        s, e = m.start(1) + offset, m.end(1) + offset
        text = text[:s] + repl + text[e:]
        offset += len(repl) - len(orig)
    # we don't fix surrounding articles after a swap — safer to leave them as-is
    return text


def _swap_city(text, n=1):    return _swap_from_list(text, _RE_CITY, GERMAN_CITIES, n)
def _swap_country(text, n=1): return _swap_from_list(text, _RE_COUNTRY, GERMAN_COUNTRIES, n)
def _swap_org(text, n=1):     return _swap_from_list(text, _RE_ORG, GERMAN_ORGS, n)


# sentence-level stuff: contradictions, deletions, duplications

_CONTRADICTIONS = [
    "Dies wurde von allen Beteiligten entschieden abgelehnt.",
    "Experten widersprechen dieser Darstellung vollständig.",
    "Tatsächlich verhält es sich genau umgekehrt.",
    "Laut neuesten Berichten ist das Gegenteil der Fall.",
    "Offizielle Quellen dementieren diese Aussage.",
    "Diese Einschätzung wird von Fachleuten als falsch eingestuft.",
    "Untersuchungen zeigen ein völlig anderes Bild.",
    "Die Datenlage widerlegt diese Behauptung eindeutig.",
    "Aktuelle Studien kommen zu gegenteiligen Schlussfolgerungen.",
    "Diese Behauptung entbehrt jeder sachlichen Grundlage.",
]


def _contradict_sents(sents: list, n: int) -> list:
    result = sents[:]
    if len(result) <= 1:
        return result
    idxs = random.sample(range(1, len(result)), min(n, len(result) - 1))
    # pick without replacement so the same contradiction doesn't show up twice in one summary
    pool = random.sample(_CONTRADICTIONS, min(len(idxs), len(_CONTRADICTIONS)))
    for i, contradiction in zip(idxs, pool):
        result[i] = contradiction
    return result


def _delete_sents(sents: list, n: int) -> list:
    if len(sents) <= 1:
        return sents
    # don't delete a sentence if the next one starts with Er/Sie/Es — would make no sense
    removable = []
    for i in range(1, len(sents)):
        follower = sents[i + 1] if i + 1 < len(sents) else ""
        if not _RE_ORPHAN_PRONOUN.match(follower):
            removable.append(i)
    if not removable:
        return sents
    to_remove = set(random.sample(removable, min(n, len(removable))))
    return [s for i, s in enumerate(sents) if i not in to_remove]


def _duplicate_sents(sents: list, n: int) -> list:
    result = sents[:]
    idxs = sorted(random.sample(range(len(result)), min(n, len(result))))
    offset = 0
    for idx in idxs:
        orig = result[idx + offset]
        words = orig.split()
        if len(words) > 5:
            # longer sentences get the "Außerdem gilt: " prefix to make the repeat less obvious
            copy = "Außerdem gilt: " + orig
        else:
            copy = orig
        result.insert(idx + 1 + offset, copy)
        offset += 1
    return result


def _fallback(text: str) -> str:
    # last resort when no numbers or entities were found to change
    sents = tokenize_sentences(text)
    sents.insert(min(1, len(sents)), random.choice(_CONTRADICTIONS))
    return " ".join(sents)


def _fallback_minor(text: str) -> str:
    # score 5 fallback: just duplicate a word, nothing dramatic
    # inserting a contradiction would push it toward score 2 territory
    words = text.split()
    if len(words) < 2:
        return text + " " + text.split()[-1] if text.split() else text
    i = random.randint(1, len(words) - 1)
    words.insert(i, words[i])
    return " ".join(words)


# faithfulness perturbation — scrambles facts at increasing severity

def perturb_faithfulness(summary: str, article: str, target_score: int) -> str:
    text = summary
    original = text

    if target_score == 5:
        ops = [
            lambda t: _perturb_year(t, -2, 2),
            lambda t: _perturb_decimal(t, 1.1, 1.5),
            lambda t: _perturb_integer(t, 0.15),
            lambda t: _perturb_percent(t, 2, 8),
            lambda t: _perturb_large_num(t, 1.1, 1.5),
        ]
        random.shuffle(ops)
        for op in ops:
            text = op(text)
            if text != original:
                break
        # use the mild fallback here, not the contradiction one
        if text == original:
            text = _fallback_minor(text)

    elif target_score == 4:
        text = _perturb_year(text, -10, 10)
        text = _perturb_decimal(text, 1.2, 2.0)
        text = _perturb_large_num(text, 1.3, 2.0)
        text = _swap_city(text, 1)
        text = _swap_country(text, 1)
        if text == original:
            text = _fallback(text)

    elif target_score == 3:
        text = _perturb_year(text, -20, 20)
        text = _perturb_decimal(text, 0.3, 0.6)
        text = _perturb_integer(text, 0.4)
        text = _perturb_large_num(text, 0.2, 0.5)
        text = _swap_city(text, 2)
        text = _swap_org(text, 1)
        sents = tokenize_sentences(text)
        sents = _contradict_sents(sents, 1)
        text = " ".join(sents)

    elif target_score == 2:
        text = _perturb_year(text, -40, 40)
        text = _perturb_decimal(text, 2.5, 5.0)
        text = _perturb_integer(text, 0.7)
        text = _perturb_large_num(text, 3.0, 6.0)
        text = _swap_city(text, 3)
        text = _swap_country(text, 2)
        text = _swap_org(text, 2)
        sents = tokenize_sentences(text)
        sents = _contradict_sents(sents, max(1, len(sents) // 2))
        text = " ".join(sents)

    elif target_score == 1:
        # score 1: everything fires
        text = _perturb_year(text, -60, 60)
        text = _perturb_decimal(text, 6.0, 12.0)
        text = _perturb_integer(text, 0.95)
        text = _perturb_large_num(text, 5.0, 10.0)
        text = _swap_city(text, 5)
        text = _swap_country(text, 5)
        text = _swap_org(text, 5)
        sents = tokenize_sentences(text)
        # delete some sentences first, then replace others with contradictions
        sents = _delete_sents(sents, max(1, len(sents) // 3))
        sents = _contradict_sents(sents, max(1, len(sents) // 2))
        text = " ".join(sents)
        # edge case: summary had nothing to perturb, force a change
        if text == original:
            text = _fallback(text)

    return text


# NRD perturbation — introduces redundancy at increasing severity

_FILLERS = [
    "das heißt also,", "mit anderen Worten,", "was bedeutet,",
    "um es noch einmal zu sagen,", "wie bereits erwähnt,",
    "wie gesagt,", "wie zuvor beschrieben,", "also nochmals,",
]

_PRONOUN_MAP = {
    r'\bEr\b': 'Der Betroffene', r'\bSie\b': 'Die Betroffene',
    r'\bEs\b': 'Das Genannte',   r'\bDies\b': 'Diese Tatsache',
    r'\bDiese\b': 'Diese genannte', r'\bDieser\b': 'Dieser genannte',
    r'\bDieses\b': 'Dieses genannte',
}

_RE_PREAMBLE = re.compile(r'^(?:hier ist|Hier ist)\b.*?[:\-]\s*$', re.IGNORECASE | re.MULTILINE)


def _nominalize(s: str) -> str:
    for pat, repl in _PRONOUN_MAP.items():
        s = re.sub(pat, repl, s)
    return s


def _add_filler(s: str) -> str:
    # grab the last clause after the final comma and repeat it
    # if there's no comma in the sentence, skip it
    base = s.rstrip('.!?')
    comma_idx = base.rfind(',')
    if comma_idx == -1:
        return s  # no comma clause found, skip filler
    tail = base[comma_idx + 1:].strip()
    if not tail:
        return s
    filler = random.choice(_FILLERS)
    return base + ' \u2014 ' + filler + ' ' + tail + '.'


def _repeat_phrase(s: str) -> str:
    base = s.rstrip('.!?')
    parts = base.split(',')
    fragment = parts[-1].strip() if len(parts) > 1 else ' '.join(base.split()[-5:])
    return base + f", also {fragment}."


def perturb_nrd(summary: str, target_score: int) -> str:
    sents = tokenize_sentences(summary)
    if not sents:
        return summary

    if target_score == 5:
        idx = random.randrange(len(sents))
        op = random.choice([_repeat_phrase, _add_filler])
        sents[idx] = op(sents[idx])

    elif target_score == 4:
        sents = _duplicate_sents(sents, 1)
        sents = [_nominalize(s) for s in sents]

    elif target_score == 3:
        sents = _duplicate_sents(sents, min(2, len(sents)))
        sents = [_add_filler(s) if random.random() < 0.5 else s for s in sents]
        sents = [_nominalize(s) for s in sents]

    elif target_score == 2:
        n_dup = max(1, int(len(sents) * 0.6))
        sents = _duplicate_sents(sents, n_dup)
        sents = [_add_filler(s) for s in sents]
        sents = [_nominalize(s) for s in sents]
        sents = [_repeat_phrase(s) for s in sents]

    elif target_score == 1:
        # strip preamble first so we don't triple "Hier ist eine Zusammenfassung:" three times
        preamble_text, content_text = _split_boilerplate(summary)
        content_sents = tokenize_sentences(content_text) if content_text else sents
        if not content_sents:
            content_sents = sents
        tripled = []
        for s in content_sents:
            s = _nominalize(s)
            s = _add_filler(s)
            s = _repeat_phrase(s)
            tripled.extend([s, s, s])
        # stick the preamble back at the front
        return (preamble_text + " ".join(tripled)) if preamble_text else " ".join(tripled)

    return " ".join(sents)


# grammaticality perturbation — introduces syntax/grammar errors

_ARTICLE_SWAPS = {
    "die": ["der", "das", "den"],
    "der": ["die", "das", "dem"],
    "das": ["die", "der", "den"],
    "den": ["die", "der", "das"],
    "dem": ["der", "die", "den"],
    "des": ["der", "die", "das"],
    "Die": ["Der", "Das", "Den"],
    "Der": ["Die", "Das", "Dem"],
    "Das": ["Die", "Der", "Den"],
}

_PREP_SWAPS = {
    "in": "auf", "auf": "in", "mit": "ohne", "ohne": "mit",
    "für": "gegen", "gegen": "für", "über": "unter", "unter": "über",
    "an": "bei", "bei": "an", "von": "durch", "durch": "von",
    "nach": "vor", "vor": "hinter", "hinter": "neben",
}

# only include Denglish words that a German speaker would actually use
_DENGLISH = ["gemanaged", "gecheckt", "gepostet", "gedownloadet", "geupdatet"]

_RE_HABEN_SEIN = re.compile(
    r'\b(hat|haben|hatte|hatten|ist|sind|war|waren)\s+(\w+(?:t|en))\b'
)

_RE_SUBCLAUSE = re.compile(
    r'((?:dass|weil|obwohl|wenn|da|damit|ob|als|wie|nachdem|bevor|bis)\s+)'
    r'([\w\s,]+?\s)'
    r'(\w+(?:t|en|iert)\.?)',
    re.IGNORECASE,
)


def _expand_contractions(text: str) -> str:
    # expand im/ins/am/etc. to long form — the uncontracted form is itself an error
    return _RE_CONTRACTION.sub(lambda m: _CONTRACTIONS[m.group(1)], text)


def _wrong_article(text: str, n: int = 1) -> str:
    # expand contractions first to expose more article targets
    text = _expand_contractions(text)
    words = text.split()
    targets = [i for i, w in enumerate(words) if w.rstrip(',') in _ARTICLE_SWAPS]
    if not targets:
        return text
    for i in random.sample(targets, min(n, len(targets))):
        key = words[i].rstrip(',')
        suffix = words[i][len(key):]
        words[i] = random.choice(_ARTICLE_SWAPS[key]) + suffix
    return ' '.join(words)


def _wrong_prep(text: str, n: int = 1) -> str:
    words = text.split()
    targets = [i for i, w in enumerate(words) if w in _PREP_SWAPS]
    if not targets:
        return text
    for i in random.sample(targets, min(n, len(targets))):
        words[i] = _PREP_SWAPS[words[i]]
    return ' '.join(words)


def _drop_auxiliary(text: str) -> str:
    def sub(m):
        return m.group(2)
    return _RE_HABEN_SEIN.sub(sub, text, count=1)


def _v2_subclause(text: str) -> str:
    def sub(m):
        end_dot = m.group(3).endswith('.')
        verb = m.group(3).rstrip('.')
        return m.group(1) + verb + " " + m.group(2).strip() + ('.' if end_dot else '')
    return _RE_SUBCLAUSE.sub(sub, text, count=1)


def _drop_function_words(sent: str, pct: float) -> str:
    stop = {
        "der","die","das","den","dem","des","ein","eine","einen","einem","einer","eines",
        "und","oder","aber","doch","auch","noch","schon","denn","weil","dass","ob",
        "in","an","auf","für","mit","von","zu","bei","nach","aus","über","unter",
        "vor","hinter","neben","zwischen","durch","gegen","ohne","um","bis","seit",
        "ist","sind","hat","haben","wird","werden","war","waren","hatte","hatten",
        "es","er","sie","wir","ihr","ich","du","man","sich","ihm","ihn",
        "nicht","kein","keine","keinen","keinem","keiner",
    }
    words = sent.split()
    result = [w for w in words if not (w.lower() in stop and random.random() < pct)]
    return ' '.join(result) if result else sent


def _shuffle_tokens(sent: str) -> str:
    words = sent.rstrip('.!?').split()
    if len(words) < 3:
        return sent
    mid = words[1:]
    random.shuffle(mid)
    return words[0] + ' ' + ' '.join(mid) + '.'


def _insert_random_function_word(sent: str) -> str:
    inserts = ["jedoch", "aber", "dennoch", "trotzdem", "zwar", "eigentlich", "schließlich"]
    words = sent.split()
    if not words:
        return sent
    pos = random.randint(1, max(1, len(words) - 1))
    words.insert(pos, random.choice(inserts))
    return ' '.join(words)


def _insert_denglish(text: str) -> str:
    # at most 1 Denglish word; only replaces verbs, never nouns
    # looks for past participles within 3 words of an auxiliary
    words = text.split()
    aux = {"hat","haben","hatte","hatten","ist","sind","war","waren","wird","werden"}
    aux_positions = {i for i, w in enumerate(words) if w.lower() in aux}
    targets = [
        i for i in range(1, len(words))
        if any(abs(i - a) <= 3 for a in aux_positions)  # within 3 words of aux
        and words[i].rstrip('.,;:!?').lower().endswith(('t', 'en'))
        and len(words[i].rstrip('.,;:!?')) > 3
        and not words[i][0].isupper()  # skip nouns
    ]
    if not targets:
        return text  # no suitable verb target, skip
    i = random.choice(targets)
    punct = words[i][len(words[i].rstrip('.,;:!?')):]
    words[i] = random.choice(_DENGLISH) + punct
    return ' '.join(words)


def _gram_fallback_minor(sent: str) -> str:
    # guaranteed minor change: swap an adjective ending
    words = sent.split()
    adj_endings = [
        ("sche", "schen"), ("ische", "ischen"), ("nde", "nden"),
        ("rte", "rten"), ("ste", "sten"), ("che", "chen"),
    ]
    for i, w in enumerate(words):
        for old_e, new_e in adj_endings:
            if w.endswith(old_e) and len(w) > len(old_e) + 2:
                words[i] = w[:-len(old_e)] + new_e
                return ' '.join(words)
    # last resort: duplicate a content word
    if len(words) >= 2:
        i = random.randrange(1, len(words))
        words.insert(i, words[i])
    return ' '.join(words)


def _count_error_sites(original: str, perturbed: str) -> int:
    # rough count: number of word positions that differ
    orig_words = original.split()
    pert_words = perturbed.split()
    diffs = sum(1 for a, b in zip(orig_words, pert_words) if a != b)
    diffs += abs(len(orig_words) - len(pert_words))
    return diffs


def perturb_grammaticality(summary: str, target_score: int) -> str:
    # strip boilerplate prefix, perturb content, reattach — preserve line breaks
    prefix, body = _split_boilerplate(summary)
    sents = tokenize_sentences(body)
    if not sents:
        return summary
    original_body = body

    if target_score == 5:
        idx = random.randrange(len(sents))
        changed = _wrong_article(sents[idx], n=1)
        if changed != sents[idx]:
            sents[idx] = changed
        elif len(sents) > 1 and random.random() < 0.5:
            # comma splice
            base = sents[idx].rstrip('.')
            nxt = sents[idx + 1] if idx + 1 < len(sents) else sents[idx - 1]
            sents[idx] = base + ', ' + nxt[0].lower() + nxt[1:]
            if idx + 1 < len(sents):
                sents.pop(idx + 1)
        else:
            sents[idx] = _gram_fallback_minor(sents[idx])

    elif target_score == 4:
        # must introduce at least 2 distinct error sites
        for i in random.sample(range(len(sents)), min(2, len(sents))):
            before = sents[i]
            for op in random.sample([
                lambda s: _wrong_article(s, n=1),
                _drop_auxiliary,
                _wrong_prep,
                _gram_fallback_minor,
            ], 3):
                result = op(sents[i])
                if result != sents[i]:
                    sents[i] = result
                    break
            if sents[i] == before:
                sents[i] = _gram_fallback_minor(sents[i])
        # verify at least 2 error sites; if not, apply a case ending error
        body_so_far = ' '.join(sents)
        if _count_error_sites(original_body, body_so_far) < 2:
            # pick a different sentence and force a prep swap or fallback
            idx2 = random.randrange(len(sents))
            result = _wrong_prep(sents[idx2])
            sents[idx2] = result if result != sents[idx2] else _gram_fallback_minor(sents[idx2])

    elif target_score == 3:
        for i, sent in enumerate(sents):
            sents[i] = _v2_subclause(sent)
            sents[i] = _wrong_article(sents[i], n=2)
            if sents[i] == sent:
                sents[i] = _gram_fallback_minor(sent)
        if len(sents) >= 2:
            j = random.randrange(len(sents) - 1)
            sents[j] = sents[j].rstrip('.') + ', ' + sents[j + 1][0].lower() + sents[j + 1][1:]
            sents.pop(j + 1)

    elif target_score == 2:
        for i, sent in enumerate(sents):
            sents[i] = _drop_function_words(sent, pct=0.30)
            sents[i] = _wrong_article(sents[i], n=2)
            sents[i] = _wrong_prep(sents[i], n=1)
        body = ' '.join(sents)
        # at most 1 Denglish word, only if a verb target exists
        body = _insert_denglish(body)
        # preserve original line breaks — rejoin using original paragraph structure
        return prefix + body

    elif target_score == 1:
        result = []
        for sent in sents:
            s = _drop_function_words(sent, pct=0.50)
            s = _shuffle_tokens(s)
            s = _insert_random_function_word(s)
            result.append(s)
        i = 0
        merged = []
        while i < len(result):
            if i + 1 < len(result) and random.random() < 0.5:
                merged.append(result[i].rstrip('.') + ' ' + result[i + 1])
                i += 2
            else:
                merged.append(result[i])
                i += 1
        return prefix + ' '.join(merged)

    body = ' '.join(sents)
    if body == original_body:
        sents[0] = _gram_fallback_minor(sents[0])
        body = ' '.join(sents)
    return prefix + body


# score assignment — distributes target scores evenly across the dataset

def assign_scores(n: int, dist: dict) -> list:
    # note: round() can be off by 1 for very small datasets (n < 20)
    # we put any remainder into the top score bucket
    assert abs(sum(dist.values()) - 1.0) < 1e-6, "Distribution must sum to 1.0"
    scores = sorted(dist.keys())
    counts, assigned = {}, 0
    for sc in scores[:-1]:
        cnt = round(dist[sc] * n)
        counts[sc] = cnt
        assigned += cnt
    counts[scores[-1]] = n - assigned
    result = []
    for sc, cnt in counts.items():
        result.extend([sc] * cnt)
    random.shuffle(result)
    return result


# file I/O

def load_jsonl(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def save_jsonl(records: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  Saved {len(records)} records -> {path}")


def append_high_scores(source_path: str, out_path: str, score_field: str, target_count: int):
    # append the high-quality originals (scores 6+7) at the bottom of the output file
    try:
        items = load_jsonl(source_path)
    except FileNotFoundError:
        print(f"  Skipping high-score append: {source_path} not found")
        return
    sixes  = [i for i in items if round(i.get(score_field, 0)) == 6]
    sevens = [i for i in items if round(i.get(score_field, 0)) == 7]
    sixes  = random.sample(sixes,  min(target_count, len(sixes)))
    sevens = random.sample(sevens, min(target_count, len(sevens)))
    with open(out_path, "a", encoding="utf-8") as f:
        for item in sixes + sevens:
            summ = fix_encoding(item.get("summary", ""))
            score = item.get(score_field)
            rec = {
                "id":                item.get("id"),
                "original_score":    score,
                "target_score":      score,
                "original_summary":  summ,
                "perturbed_summary": summ,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"  Appended {len(sixes)} sixes + {len(sevens)} sevens from {source_path}")


# main pipeline functions — one per dimension

def process_faithfulness(inp: str, out: str, dist: dict = SCORE_DISTRIBUTION):
    print(f"\n-- Faithfulness: {inp}")
    items = load_jsonl(inp)
    scores = assign_scores(len(items), dist)
    records = []
    changed = 0
    for item, target in zip(items, scores):
        summ = fix_encoding(item.get("summary", ""))
        art  = fix_encoding(item.get("article", ""))
        pert = perturb_faithfulness(summ, art, target)
        if pert != summ:
            changed += 1
        records.append({
            "id":                item.get("id"),
            "original_score":    item.get("faithfulness_score"),
            "target_score":      target,
            "original_summary":  summ,
            "perturbed_summary": pert,
        })
    df = pd.DataFrame(records)
    print(f"  Changed: {changed}/{len(records)} summaries")
    print(f"  Score distribution:\n{df['target_score'].value_counts().sort_index().to_string()}")
    save_jsonl(records, out)
    append_high_scores("faithfulness_rating_6_7.jsonl", out, "faithfulness_score", len(records) // len(SCORE_DISTRIBUTION))
    return df


def process_nrd(inp: str, out: str, dist: dict = SCORE_DISTRIBUTION):
    print(f"\n-- NRD: {inp}")
    items = load_jsonl(inp)
    scores = assign_scores(len(items), dist)
    records = []
    for item, target in zip(items, scores):
        summ = fix_encoding(item.get("summary", ""))
        pert = perturb_nrd(summ, target)
        records.append({
            "id":                item.get("id"),
            "original_score":    item.get("non_redundancy_score"),
            "target_score":      target,
            "original_summary":  summ,
            "perturbed_summary": pert,
        })
    df = pd.DataFrame(records)
    print(f"  Score distribution:\n{df['target_score'].value_counts().sort_index().to_string()}")
    save_jsonl(records, out)
    append_high_scores("nrd_rating_6_7.jsonl", out, "non_redundancy_score", len(records) // len(SCORE_DISTRIBUTION))
    return df


def process_grammaticality(inp: str, out: str, dist: dict = SCORE_DISTRIBUTION):
    print(f"\n-- Grammaticality: {inp}")
    items = load_jsonl(inp)
    scores = assign_scores(len(items), dist)
    records = []
    changed = 0
    for item, target in zip(items, scores):
        summ = fix_encoding(item.get("summary", ""))
        pert = perturb_grammaticality(summ, target)
        if pert != summ:
            changed += 1
        records.append({
            "id":                item.get("id"),
            "original_score":    item.get("grammaticality_score"),
            "target_score":      target,
            "original_summary":  summ,
            "perturbed_summary": pert,
        })
    if not records:
        print("  No records to process.")
        return pd.DataFrame()
    df = pd.DataFrame(records)
    print(f"  Changed: {changed}/{len(records)} summaries")
    print(f"  Score distribution:\n{df['target_score'].value_counts().sort_index().to_string()}")
    save_jsonl(records, out)
    append_high_scores("grammaticality_rating_6_7.jsonl", out, "grammaticality_score", len(records) // len(SCORE_DISTRIBUTION))
    return df


# CLI entry point

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input_faith", default="adv_proj_faithfulness.jsonl")
    p.add_argument("--input_nrd",   default="adv_proj_nrd.jsonl")
    p.add_argument("--input_gram",  default="adv_proj_grammaticality.jsonl")
    p.add_argument("--out_faith",   default="perturbed_faithfulness.jsonl")
    p.add_argument("--out_nrd",     default="perturbed_nrd.jsonl")
    p.add_argument("--out_gram",    default="perturbed_grammaticality.jsonl")
    p.add_argument("--seed", type=int, default=RANDOM_SEED)
    p.add_argument("--test", action="store_true", help="run _v2_subclause self-test and exit")
    args = p.parse_args()

    if args.test:
        # quick check to see if the subclause regex is actually firing
        test_cases = [
            "Er sagte, dass die Regierung das Gesetz verabschiedet.",
            "Sie glaubt, weil er die Wahrheit gesagt hat.",
            "Das Projekt scheiterte, obwohl das Team hart gearbeitet hatte.",
        ]
        print("_v2_subclause self-test:")
        for sent in test_cases:
            result = _v2_subclause(sent)
            matched = "MATCHED" if result != sent else "no match"
            print(f"  [{matched}]")
            print(f"    orig: {sent}")
            print(f"    pert: {result}")
        import sys; sys.exit(0)

    random.seed(args.seed)
    np.random.seed(args.seed)

    print(f"Score distribution: {SCORE_DISTRIBUTION}")
    df_f = process_faithfulness(args.input_faith, args.out_faith)
    df_n = process_nrd(args.input_nrd, args.out_nrd)
    df_g = process_grammaticality(args.input_gram, args.out_gram)
    print(f"\nDone.  Faith: {len(df_f)} | NRD: {len(df_n)} | Gram: {len(df_g)}")
