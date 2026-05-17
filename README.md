# WordCrafter: TextTwist Challenge

A classic word puzzle game inspired by TextTwist, built with Python and Pygame. Find words using scrambled letters, discover the main word, and advance through challenging levels!

## 🎮 Game Features

### Core Gameplay
- **Classic TextTwist Experience**: Form 3-7 letter words from scrambled letters
- **Main Word Challenge**: Find the 6-letter main word to advance levels
- **Progressive Difficulty**: More words required as you advance
- **Timer Pressure**: 2-3 minute rounds with visual warnings
- **Smart Scoring**: Exponential points for longer words

### Visual Features
- **Word Blanks Grid**: See `_ _ _ _` for unfound words, filled when discovered
- **Animated Interface**: Letter bouncing, score popups, smooth transitions
- **Color-Coded Progress**: Main word highlighted in gold, found words in green
- **Real-time Stats**: Completion percentage, level progress, timer warnings

### Game Mechanics
- **No-Penalty Shuffling**: Rearrange letters anytime with smooth animations
- **Hint System**: Get clues for unfound words (limited uses)
- **Achievement System**: Unlock badges for various milestones
- **Level Progression**: Traditional advancement requiring main word + minimum others

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TextTwist
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**
   ```bash
   python main.py
   ```

## 🎯 How to Play

### Objective
- Form words (3-7 letters) using the given scrambled letters
- Find the main 6-letter word to advance to the next level
- Meet the minimum word requirement for each level
- Score points based on word length and speed

### Controls
- **Mouse**: Click letters to form words
- **Keyboard**: Type letters directly
- **ENTER**: Submit current word
- **SPACE**: Shuffle letters
- **BACKSPACE**: Remove last letter
- **H**: Use hint (limited)
- **ESC**: Return to main menu

### Scoring System
- **3-letter words**: 100 points
- **4-letter words**: 400 points
- **5-letter words**: 800 points
- **6-letter words**: 1,600 points
- **7-letter words**: 3,200 points
- **Time Bonus**: 10% per 10 seconds remaining
- **Main Word Bonus**: +2,000 points
- **Perfect Round**: +5,000 points for finding all words

## 📁 Project Structure

```
TextTwist/
├── main.py              # Main game file
├── word_validator.py    # Word validation and dictionary management
├── words.txt           # Word dictionary (auto-generated)
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── build/             # Build artifacts (web deployment)
```

## 🛠️ Development

### Running in Development Mode
```bash
# Install development dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Code Structure
- **main.py**: Contains the main `WordCrafter` class with game logic, UI, and state management
- **word_validator.py**: Handles word validation, dictionary loading, and word generation
- **SoundManager**: Placeholder system for future sound integration

### Adding New Features
1. **New Game Modes**: Extend the state system in `main.py`
2. **Sound Effects**: Implement actual sound files in the `SoundManager` class
3. **New Achievements**: Add to the achievements dictionary
4. **Custom Dictionaries**: Modify `word_validator.py` to load custom word lists

## 🌐 Web Deployment

The game is designed to be deployable to the web using Pygbag:

```bash
# Install pygbag
pip install pygbag

# Build for web
pygbag main.py
```

## 🎨 Customization

### Settings
Access the in-game settings to customize:
- **Sound**: Enable/disable audio feedback
- **Timer**: Adjust round duration (2-5 minutes)
- **Difficulty**: Choose challenge level

### Themes
The game uses a classic TextTwist color scheme:
- **Background**: Blue gradient
- **Letters**: White circles with hover effects
- **Found Words**: Green highlighting
- **Main Word**: Gold highlighting

## 🏆 Achievements

Unlock various achievements by:
- Finding your first word
- Discovering 10+ words in one game
- Finding 7-letter words
- Reaching higher levels
- Perfect rounds (finding all words)
- Speed challenges

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Known Issues

- Sound system is currently a placeholder (no actual audio)
- Web deployment requires pygbag setup
- Dictionary is basic (can be expanded with larger word lists)

## 📞 Support

If you encounter any issues or have suggestions, please open an issue on the repository.

---

**Enjoy playing WordCrafter!** 🎉
=======
# wordcraft
This is a TextTwist inspired game. It's only a school project and it's good to show some concepts of parallel and distributed computing.
