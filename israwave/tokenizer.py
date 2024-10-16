import re
from .symbols import phonemes_to_ids
from israwave.logging import log

WHITESPACE_RE = re.compile(r"\s+")

rules = [
    ["ˈalef", ""],
    ["jˈod", "i"],
    ["tˈav", "t"],
    ["mˈem", "m"],
    ["ʁˈejʃ", "ʁ"],
    ["vˈet", "v"],
    ["bˈet", "b"],
    ["gˈimel", "g"],
    ["ɡˈimel", "g"],
    ["dˈalet", "d"],
    ["hˈe", "h"],
    ["vˈav", "v"],
    ["zˈajin", "z"],
    ["χˈet", "χ"],
    ["tˈet", "t"],
    ["χˈaf", "χ"],
    ["lˈamed", "l"],
    ["nˈun", "n"],
    ["sˈameχ", "s"],
    ["ˈajin", ""],
    ["fˈe", "f"],
    ["pˈe", "p"],
    ["tsˈadi", "t"],
    ["kˈof", "k"],
    ["ʃˈin", "ʃ"],
    ["sˈin", "s"],
    ############
    ["ʃvˈɑ", ""],
    ["ʃvˈa", ""],
    ["dˈaɡɛʃ", ""],
    ["dˈagɛʃ", ""],
    ############
    ["hˈiːbɹuː", ""],
]

class IPATokenizer:
    def __init__(self, espeak_data_path = None) -> None:
        self.espeak_data_path = espeak_data_path
    
    def preprocess_text(self, text, _language):
        return self.collapse_whitespace(text)
    
    def collapse_whitespace(self, text):
        text = re.sub(WHITESPACE_RE, " ", text)
        return text
    
    def phonemize_text(self, text: str, language: str) -> str:
        try:
            from piper_phonemize import phonemize_espeak
        except ImportError:
            raise ImportError(
                "piper-phonemize package is needed for the IPA tokenizer.\n"
                "pip install piper-phonemize\n"
                "or build it yourself from the following repository:\n"
                "https://github.com/rhasspy/piper-phonemize"
            )

        # Preprocess
        text = self.preprocess_text(text, language)
        # Phonemize        
        phonemes = phonemize_espeak(text, language, data_path=self.espeak_data_path)
        new_phonemes = []
        for phones in phonemes:
            str = ' ' + ' '.join(phones) + ' '
            for rule in rules:
                fromPhones = [x for x in rule[0]]
                toPhones = [x for x in rule[1]]
                fromStr = ' ' + ' '.join(fromPhones) + ' '
                toStr = ' ' if not toPhones else ' ' + ' '.join(toPhones) + ' '
                str = re.sub(fromStr, toStr, str)
            new_phonemes.append(str.strip().split(' '))
        return new_phonemes, text
    
    def tokenize(self, text, language):
        try:
            # Accept phonemes directly
            phoneme_ids, normalized_text = phonemes_to_ids(text), self.preprocess_text(text, 'he')
        except:
            # Create phoenems
            phonemes, normalized_text = self.phonemize_text(text, language)
            phonemes = [phoneme for sentence_phonemes in phonemes for phoneme in sentence_phonemes]
            phonemes = list(self.collapse_whitespace("".join(phonemes)))
            phoneme_ids = phonemes_to_ids(phonemes)
            log.debug(f"phonemes: {''.join(phonemes)} text: {text}")
        return phoneme_ids, normalized_text