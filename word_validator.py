import os
import threading

class WordValidator:
    def __init__(self, dictionary_file="words.txt"):
        self.words = set()
        self.long_words = []
        self.load_dictionary(dictionary_file)
    
    def load_dictionary(self, dictionary_file):
        # Default dictionary if file doesn't exist
        if not os.path.exists(dictionary_file):
            self._create_default_dictionary(dictionary_file)
        
        # Load dictionary in a separate thread
        thread = threading.Thread(target=self._load_dictionary_thread, args=(dictionary_file,))
        thread.daemon = True
        thread.start()
    
    def _load_dictionary_thread(self, dictionary_file):
        with open(dictionary_file, 'r') as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    self.words.add(word)
                    if 6 <= len(word) <= 7:
                        self.long_words.append(word)
    
    def _create_default_dictionary(self, dictionary_file):
        # Create a comprehensive dictionary focused on 3-7 letter words for TextTwist
        default_words = [
            # 3-letter words
            "cat", "dog", "run", "sun", "fun", "car", "bar", "far", "war", "art",
            "eat", "bat", "hat", "rat", "sat", "mat", "fat", "pat", "net", "set",
            "get", "let", "met", "pet", "wet", "yet", "bit", "fit", "hit", "kit",
            "lit", "pit", "sit", "wit", "cut", "but", "gut", "hut", "nut", "put",
            "lot", "hot", "pot", "rot", "got", "not", "dot", "cot", "top", "hop",
            "cop", "pop", "mop", "sop", "lap", "cap", "gap", "map", "nap", "rap",
            "sap", "tap", "zip", "tip", "rip", "hip", "dip", "lip", "sip", "win",
            "bin", "din", "fin", "pin", "sin", "tin", "can", "fan", "man", "pan",
            "ran", "tan", "van", "ban", "den", "hen", "men", "pen", "ten", "when",

            # 4-letter words
            "word", "time", "work", "life", "hand", "part", "head", "face", "fact",
            "place", "right", "great", "small", "large", "next", "early", "young",
            "important", "few", "public", "bad", "same", "able", "woman", "here",
            "should", "home", "give", "air", "line", "set", "own", "under", "read",
            "last", "never", "us", "left", "end", "why", "turn", "start", "might",
            "story", "saw", "far", "sea", "draw", "left", "late", "run", "don't",
            "while", "press", "close", "night", "real", "life", "few", "north",
            "book", "carry", "took", "science", "eat", "room", "friend", "began",
            "idea", "fish", "mountain", "stop", "once", "base", "hear", "horse",
            "cut", "sure", "watch", "color", "wood", "main", "enough", "plain",
            "girl", "usual", "young", "ready", "above", "ever", "red", "list",
            "though", "feel", "talk", "bird", "soon", "body", "dog", "family",
            "direct", "leave", "song", "measure", "door", "product", "black",
            "short", "numeral", "class", "wind", "question", "happen", "complete",

            # 5-letter words
            "about", "other", "which", "their", "would", "there", "could", "first",
            "after", "these", "think", "where", "being", "every", "great", "might",
            "shall", "still", "those", "come", "state", "never", "become", "between",
            "high", "really", "something", "most", "another", "much", "family",
            "own", "out", "leave", "put", "old", "while", "mean", "on", "keep",
            "student", "why", "let", "great", "same", "big", "group", "begin",
            "seem", "country", "help", "talk", "turn", "ask", "made", "point",
            "little", "too", "each", "right", "program", "here", "so", "question",
            "work", "life", "become", "day", "get", "has", "him", "his", "how",
            "man", "new", "now", "old", "see", "two", "way", "who", "boy", "did",
            "its", "let", "put", "say", "she", "too", "use", "her", "many", "some",
            "time", "very", "when", "come", "could", "do", "first", "get", "give",
            "go", "have", "him", "how", "know", "like", "look", "make", "most",
            "over", "said", "some", "take", "than", "them", "well", "were",

            # 6-letter words
            "people", "before", "should", "through", "just", "where", "much", "good",
            "sentence", "man", "think", "say", "great", "where", "help", "through",
            "much", "before", "line", "right", "too", "means", "old", "any", "same",
            "tell", "boy", "follow", "came", "want", "show", "also", "around",
            "form", "three", "small", "set", "put", "end", "why", "again", "turn",
            "here", "why", "ask", "went", "men", "read", "need", "land", "different",
            "home", "us", "move", "try", "kind", "hand", "picture", "again", "change",
            "off", "play", "spell", "air", "away", "animal", "house", "point",
            "page", "letter", "mother", "answer", "found", "study", "still", "learn",
            "should", "America", "world", "high", "every", "near", "add", "food",
            "between", "own", "below", "country", "plant", "last", "school", "father",
            "keep", "tree", "never", "start", "city", "earth", "eye", "light",
            "thought", "head", "under", "story", "saw", "left", "don't", "few",
            "while", "along", "might", "close", "something", "seem", "next", "hard",
            "open", "example", "begin", "life", "always", "those", "both", "paper",
            "together", "got", "group", "often", "run", "important", "until", "children",
            "side", "feet", "car", "mile", "night", "walk", "white", "sea", "began",
            "grow", "took", "river", "four", "carry", "state", "once", "book",
            "hear", "stop", "without", "second", "later", "miss", "idea", "enough",
            "eat", "face", "watch", "far", "Indian", "really", "almost", "let",
            "above", "girl", "sometimes", "mountain", "cut", "young", "talk", "soon",
            "list", "song", "being", "leave", "family", "it's",

            # 7-letter words
            "another", "between", "through", "because", "around", "before", "picture",
            "sentence", "example", "thought", "without", "important", "children",
            "different", "following", "complete", "against", "nothing", "someone",
            "toward", "however", "several", "remember", "possible", "problem",
            "develop", "during", "follow", "learning", "came", "show", "large",
            "public", "ability", "become", "already", "receive", "family", "across",
            "member", "program", "believe", "happen", "special", "working", "moment",
            "general", "feeling", "getting", "nothing", "making", "together", "business",
            "looking", "number", "writing", "water", "called", "first", "people",
            "other", "after", "first", "also", "back", "other", "many", "family",
            "own", "out", "leave", "put", "old", "while", "mean", "on", "keep",
            "student", "why", "let", "great", "same", "big", "group", "begin"
        ]
        
        with open(dictionary_file, 'w') as f:
            for word in default_words:
                f.write(word + '\n')
        
        self.words = set(default_words)
        # For TextTwist, long words are 6-7 letters (main words for gameplay)
        self.long_words = [word for word in default_words if 6 <= len(word) <= 7]
    
    def is_valid_word(self, word):
        return word.lower() in self.words
    
    def get_long_words(self):
        return self.long_words if self.long_words else ["people", "before", "through"]
    
    def get_possible_words(self, letters):
        """Find all possible words that can be formed from the given letters"""
        possible_words = []
        letters_lower = letters.lower()
        
        # Use threading to process in chunks for better performance
        def process_chunk(word_chunk, result_list):
            for word in word_chunk:
                if self._can_form_word(word, letters_lower):
                    result_list.append(word)
        
        # Split dictionary into chunks for parallel processing
        word_list = list(self.words)
        chunk_size = max(1, len(word_list) // 4)
        chunks = [word_list[i:i + chunk_size] for i in range(0, len(word_list), chunk_size)]
        
        results = [[] for _ in range(len(chunks))]
        threads = []
        
        for i, chunk in enumerate(chunks):
            thread = threading.Thread(target=process_chunk, args=(chunk, results[i]))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        for result in results:
            possible_words.extend(result)
        
        return sorted(possible_words, key=len, reverse=True)
    
    def _can_form_word(self, word, letters):
        """Check if a word can be formed from the given letters"""
        letter_count = {}
        for letter in letters:
            letter_count[letter] = letter_count.get(letter, 0) + 1
        
        for letter in word:
            if letter not in letter_count or letter_count[letter] == 0:
                return False
            letter_count[letter] -= 1
        
        return True