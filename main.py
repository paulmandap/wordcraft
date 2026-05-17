import asyncio
import pygame
import random
import os
import math
from word_validator import WordValidator

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.initialize_sounds()

    def initialize_sounds(self):
        """Initialize sound effects - simplified version"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            # For now, just create placeholder sounds (no actual sound generation)
            # In a full implementation, you would load sound files here
            self.sounds = {
                'click': None,
                'valid_word': None,
                'invalid_word': None,
                'shuffle': None,
                'timer_warning': None,
                'level_up': None
            }
        except pygame.error:
            # If sound initialization fails, disable sounds
            self.enabled = False

    def play_sound(self, sound_name):
        """Play a sound effect if sounds are enabled (placeholder for now)"""
        # In a full implementation, this would play actual sound files
        # For now, we just pass to avoid errors
        pass

    def set_enabled(self, enabled):
        """Enable or disable sound effects"""
        self.enabled = enabled

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Text Twist 2 Color Scheme
GRADIENT_TOP = (70, 130, 180)      # Steel Blue
GRADIENT_BOTTOM = (25, 25, 112)    # Midnight Blue
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
LETTER_CIRCLE_COLOR = (255, 255, 255)
LETTER_CIRCLE_BORDER = (200, 200, 200)
LETTER_HOVER_COLOR = (255, 255, 200)
CURRENT_WORD_BG = (135, 206, 235)  # Sky Blue
FOUND_WORD_BG = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 149, 237)

# Layout Constants
FONT_SIZE = 28
BIG_FONT_SIZE = 48
LETTER_CIRCLE_RADIUS = 30
LETTER_SPACING = 80
CURRENT_WORD_HEIGHT = 50
WORD_GRID_CELL_WIDTH = 80
WORD_GRID_CELL_HEIGHT = 35
BUTTON_HEIGHT = 40
GAME_TIME = 180  # 3 minutes

# Game States
MENU_STATE = "menu"
INSTRUCTIONS_STATE = "instructions"
SETTINGS_STATE = "settings"
GAME_STATE = "game"
LEVEL_COMPLETE_STATE = "level_complete"
GAME_OVER_STATE = "game_over"

class WordCrafter:
    def __init__(self):
        self.screen = None
        self.clock = None
        self.font = None
        self.big_font = None
        self.small_font = None
        self.running = True
        self.current_state = MENU_STATE
        self.validator = WordValidator()
        self.sound_manager = SoundManager()

        # Game state
        self.letters = []
        self.current_word = ""
        self.found_words = []
        self.score = 0
        self.time_left = GAME_TIME
        self.last_time_update = 0
        self.hovered_letter = -1  # For hover effects
        self.shuffle_button_rect = None
        self.clear_button_rect = None
        self.hint_button_rect = None

        # Settings
        self.settings = {
            'sound_enabled': True,
            'theme': 'classic',
            'difficulty': 'normal',
            'timer_duration': 180
        }

        # Level progression - Traditional TextTwist style
        self.current_level = 1
        self.words_needed_to_advance = 3  # Start with easier requirement
        self.total_score = 0

        # Word tracking for blanks display
        self.all_possible_words = []
        self.words_by_length = {}
        self.main_word = ""  # The original word that letters came from
        self.found_main_word = False

        # Hint system
        self.hints_available = 3
        self.hint_used_this_round = False
        self.hint_message = ""
        self.hint_display_time = 0

        # Timer warning system
        self.timer_warning_active = False
        self.last_warning_time = 0

        # Animation system
        self.animations = {
            'letter_bounce': {},  # Track bouncing letters
            'word_flash': 0,      # Flash effect for submitted words
            'score_popup': [],    # Score popup animations
            'screen_transition': 0  # Screen transition effect
        }
        self.animation_time = 0

        # Achievement system
        self.achievements = {
            'first_word': {'unlocked': False, 'name': 'First Word', 'description': 'Submit your first word'},
            'word_master': {'unlocked': False, 'name': 'Word Master', 'description': 'Find 10 words in one game'},
            'speed_demon': {'unlocked': False, 'name': 'Speed Demon', 'description': 'Submit a word in under 5 seconds'},
            'long_word': {'unlocked': False, 'name': 'Wordsmith', 'description': 'Find a 7+ letter word'},
            'level_5': {'unlocked': False, 'name': 'Rising Star', 'description': 'Reach level 5'},
            'perfect_round': {'unlocked': False, 'name': 'Perfect Round', 'description': 'Find all possible words in a round'},
            'hint_master': {'unlocked': False, 'name': 'Hint Master', 'description': 'Use all your hints in one game'},
            'time_master': {'unlocked': False, 'name': 'Time Master', 'description': 'Complete a level with 2+ minutes remaining'}
        }
        self.achievement_popup = None
        self.achievement_popup_time = 0
        
    async def initialize(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("WordCrafter: Text Twist Challenge")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', FONT_SIZE, bold=True)
        self.big_font = pygame.font.SysFont('Arial', BIG_FONT_SIZE, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 20, bold=True)
        
    def start_new_game(self):
        # Traditional TextTwist: Start with 6-letter words (3-7 letter range)
        # Focus on 6-letter words as the main challenge
        available_words = [w for w in self.validator.get_long_words() if len(w) == 6]
        if not available_words:
            # Fallback to 7-letter words if no 6-letter words available
            available_words = [w for w in self.validator.get_long_words() if len(w) == 7]
        if not available_words:
            # Final fallback to any available long words
            available_words = self.validator.get_long_words()

        word = random.choice(available_words)
        self.main_word = word.lower()  # Store the main word
        self.letters = list(word.upper())
        random.shuffle(self.letters)
        self.found_main_word = False

        # Calculate all possible words for this letter set
        letters_str = ''.join(self.letters).lower()
        self.all_possible_words = self.validator.get_possible_words(letters_str)
        # Filter to only include words of 3-7 letters (classic TextTwist range)
        self.all_possible_words = [w for w in self.all_possible_words if 3 <= len(w) <= 7]

        # Group words by length for display
        self.words_by_length = {}
        for possible_word in self.all_possible_words:
            length = len(possible_word)
            if length not in self.words_by_length:
                self.words_by_length[length] = []
            self.words_by_length[length].append(possible_word)

        self.current_word = ""
        self.found_words = []
        self.score = 0
        self.time_left = self.settings['timer_duration']
        self.last_time_update = pygame.time.get_ticks()
        self.current_state = GAME_STATE
        self.hint_used_this_round = False
        
    def update_time(self):
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.last_time_update) / 1000  # Convert to seconds

        # Check for timer warnings in last 10 seconds
        if self.time_left <= 10 and self.time_left > 0:
            if not self.timer_warning_active:
                self.timer_warning_active = True
                if self.settings['sound_enabled']:
                    self.sound_manager.play_sound('timer_warning')

            # Flash warning every second in last 10 seconds
            if int(self.time_left) != self.last_warning_time:
                self.last_warning_time = int(self.time_left)
                if self.settings['sound_enabled']:
                    self.sound_manager.play_sound('click')
        else:
            self.timer_warning_active = False

        self.time_left -= elapsed
        self.last_time_update = current_time

        if self.time_left <= 0:
            self.time_left = 0
            self.current_state = GAME_OVER_STATE
    
    def add_letter(self, letter):
        if letter in self.letters:
            temp_letters = self.letters.copy()
            temp_current = self.current_word
            
            # Check if we have enough of this letter
            letter_count_in_current = temp_current.count(letter)
            letter_count_in_available = temp_letters.count(letter)
            
            if letter_count_in_current < letter_count_in_available:
                self.current_word += letter
                if self.settings['sound_enabled']:
                    self.sound_manager.play_sound('click')
                # Find the letter index and add bounce animation
                for i, l in enumerate(self.letters):
                    if l == letter and i not in self.animations['letter_bounce']:
                        self.add_letter_bounce(i)
                        break
                
    def remove_last_letter(self):
        if self.current_word:
            self.current_word = self.current_word[:-1]
    
    def submit_word(self):
        # Enforce minimum 3-letter requirement
        if len(self.current_word) < 3:
            if len(self.current_word) > 0:
                # Show feedback for too short words
                self.add_score_popup("TOO SHORT!", SCREEN_WIDTH // 2, 250)
                if self.settings['sound_enabled']:
                    self.sound_manager.play_sound('invalid_word')
            return

        # Check if word already found
        if self.current_word.lower() in self.found_words:
            self.add_score_popup("ALREADY FOUND!", SCREEN_WIDTH // 2, 250)
            if self.settings['sound_enabled']:
                self.sound_manager.play_sound('invalid_word')
            return

        # Check if word is valid using the validator
        if self.validator.is_valid_word(self.current_word.lower()):
            self.found_words.append(self.current_word.lower())

            # Traditional TextTwist scoring system (optimized for 3-7 letters)
            word_length = len(self.current_word)

            # Base points: 3-letter=100, 4-letter=400, 5-letter=800, 6-letter=1600, 7-letter=3200
            if word_length == 3:
                base_score = 100
            elif word_length == 4:
                base_score = 400
            elif word_length == 5:
                base_score = 800
            elif word_length == 6:
                base_score = 1600
            elif word_length == 7:
                base_score = 3200
            else:
                # Fallback for any words outside 3-7 range (shouldn't happen now)
                base_score = 100 * (word_length ** 2)

            # Time bonus: 10% of base score for each 10 seconds remaining
            time_bonus_multiplier = max(0, int(self.time_left / 10)) * 0.1
            time_bonus = int(base_score * time_bonus_multiplier)

            # Level multiplier (small bonus for higher levels)
            level_multiplier = 1 + (self.current_level - 1) * 0.1

            total_points = int((base_score + time_bonus) * level_multiplier)
            self.score += total_points
            self.total_score += total_points

            # Play success sound and add visual effects
            if self.settings['sound_enabled']:
                self.sound_manager.play_sound('valid_word')

            # Add visual effects
            self.add_word_flash()
            self.add_score_popup(total_points, SCREEN_WIDTH // 2, 250)

            # Check if this is the main word (6+ letters from original set)
            if self.current_word.lower() == self.main_word:
                self.found_main_word = True
                self.add_score_popup("MAIN WORD FOUND!", SCREEN_WIDTH // 2, 220)
                # Bonus points for finding the main word
                main_word_bonus = 2000
                self.score += main_word_bonus
                self.total_score += main_word_bonus
                self.add_score_popup(f"+{main_word_bonus} BONUS!", SCREEN_WIDTH // 2, 190)
            elif word_length >= 6:
                self.add_score_popup(f"{word_length}-LETTER WORD!", SCREEN_WIDTH // 2, 220)

            self.current_word = ""

            # Check for completion bonus (all words found)
            if len(self.found_words) == len(self.all_possible_words):
                completion_bonus = 5000 + (self.current_level * 1000)
                self.score += completion_bonus
                self.total_score += completion_bonus
                self.add_score_popup(f"PERFECT! +{completion_bonus}", SCREEN_WIDTH // 2, 200)

            # Check achievements
            self.check_achievements()

            # Check for level advancement (must find main word + minimum other words)
            if self.found_main_word and len(self.found_words) >= self.words_needed_to_advance:
                self.advance_level()
        else:
            # Play error sound for invalid words
            if self.settings['sound_enabled']:
                self.sound_manager.play_sound('invalid_word')

    def shuffle_letters(self):
        """Shuffle the available letters with no penalty"""
        random.shuffle(self.letters)
        if self.settings['sound_enabled']:
            self.sound_manager.play_sound('shuffle')

        # Add bounce animation to all letters when shuffled
        for i in range(len(self.letters)):
            self.add_letter_bounce(i)

        # Show shuffle feedback
        self.add_score_popup("SHUFFLED!", SCREEN_WIDTH // 2, 350)

    def clear_current_word(self):
        """Clear the current word being formed"""
        self.current_word = ""

    def advance_level(self):
        """Advance to the next level with traditional TextTwist progression"""
        self.current_level += 1

        # Increase difficulty by requiring more words (traditional progression)
        if self.current_level <= 3:
            self.words_needed_to_advance = 3
        elif self.current_level <= 6:
            self.words_needed_to_advance = 4
        elif self.current_level <= 10:
            self.words_needed_to_advance = 5
        else:
            self.words_needed_to_advance = min(6 + (self.current_level - 10), 10)

        # Add time bonus for completing level (traditional 30 seconds)
        self.time_left += 30

        # Level completion bonus
        level_bonus = 1000 * self.current_level
        self.score += level_bonus
        self.total_score += level_bonus

        # Play level up sound
        if self.settings['sound_enabled']:
            self.sound_manager.play_sound('level_up')
        # Show level complete screen
        self.current_state = LEVEL_COMPLETE_STATE

    def use_hint(self):
        """Use a hint to reveal word lengths or give clues"""
        if self.hints_available > 0 and not self.hint_used_this_round:
            self.hints_available -= 1
            self.hint_used_this_round = True

            # Get all possible words from current letters
            letters_str = ''.join(self.letters).lower()
            possible_words = self.validator.get_possible_words(letters_str)

            # Filter out already found words
            unfound_words = [word for word in possible_words if word not in self.found_words and len(word) >= 3]

            if unfound_words:
                # Choose a random unfound word and reveal its length and first letter
                hint_word = random.choice(unfound_words)
                self.hint_message = f"Try a {len(hint_word)}-letter word starting with '{hint_word[0].upper()}'"
                self.hint_display_time = 5.0  # Show hint for 5 seconds

                # Add visual effect
                self.add_score_popup(f"HINT: {len(hint_word)} letters", SCREEN_WIDTH // 2, 200)

                if self.settings['sound_enabled']:
                    self.sound_manager.play_sound('click')

                return True
            else:
                # No more hints available
                self.hint_message = "No more hints available!"
                self.hint_display_time = 3.0
                return False
        return False

    def update_animations(self, dt):
        """Update all animations"""
        self.animation_time += dt

        # Update letter bounce animations
        for letter_index in list(self.animations['letter_bounce'].keys()):
            self.animations['letter_bounce'][letter_index] -= dt
            if self.animations['letter_bounce'][letter_index] <= 0:
                del self.animations['letter_bounce'][letter_index]

        # Update word flash effect
        if self.animations['word_flash'] > 0:
            self.animations['word_flash'] -= dt

        # Update score popup animations
        self.animations['score_popup'] = [
            (text, x, y, time - dt, alpha)
            for text, x, y, time, alpha in self.animations['score_popup']
            if time - dt > 0
        ]

        # Update screen transition
        if self.animations['screen_transition'] > 0:
            self.animations['screen_transition'] -= dt

        # Update hint message display
        if self.hint_display_time > 0:
            self.hint_display_time -= dt

        # Update achievement popup
        if self.achievement_popup_time > 0:
            self.achievement_popup_time -= dt

    def add_letter_bounce(self, letter_index):
        """Add bounce animation to a letter"""
        self.animations['letter_bounce'][letter_index] = 0.3

    def add_word_flash(self):
        """Add flash effect for word submission"""
        self.animations['word_flash'] = 0.5

    def add_score_popup(self, points, x, y):
        """Add score popup animation"""
        self.animations['score_popup'].append((f"+{points}", x, y, 2.0, 255))

    def start_screen_transition(self):
        """Start screen transition effect"""
        self.animations['screen_transition'] = 0.3

    def check_achievements(self):
        """Check and unlock achievements"""
        # First word achievement
        if not self.achievements['first_word']['unlocked'] and len(self.found_words) >= 1:
            self.unlock_achievement('first_word')

        # Word master achievement
        if not self.achievements['word_master']['unlocked'] and len(self.found_words) >= 10:
            self.unlock_achievement('word_master')

        # Long word achievement
        if not self.achievements['long_word']['unlocked']:
            for word in self.found_words:
                if len(word) >= 7:
                    self.unlock_achievement('long_word')
                    break

        # Level 5 achievement
        if not self.achievements['level_5']['unlocked'] and self.current_level >= 5:
            self.unlock_achievement('level_5')

        # Time master achievement (check when advancing level)
        if not self.achievements['time_master']['unlocked'] and self.time_left >= 120:
            self.unlock_achievement('time_master')

        # Perfect round achievement
        if not self.achievements['perfect_round']['unlocked'] and len(self.found_words) == len(self.all_possible_words):
            self.unlock_achievement('perfect_round')

    def unlock_achievement(self, achievement_id):
        """Unlock an achievement and show popup"""
        if achievement_id in self.achievements and not self.achievements[achievement_id]['unlocked']:
            self.achievements[achievement_id]['unlocked'] = True
            self.achievement_popup = self.achievements[achievement_id]
            self.achievement_popup_time = 4.0  # Show for 4 seconds

            # Play achievement sound
            if self.settings['sound_enabled']:
                self.sound_manager.play_sound('level_up')

    def draw_gradient_background(self):
        """Draw the signature blue gradient background"""
        for y in range(SCREEN_HEIGHT):
            # Calculate the blend ratio
            ratio = y / SCREEN_HEIGHT
            # Interpolate between top and bottom colors
            r = int(GRADIENT_TOP[0] * (1 - ratio) + GRADIENT_BOTTOM[0] * ratio)
            g = int(GRADIENT_TOP[1] * (1 - ratio) + GRADIENT_BOTTOM[1] * ratio)
            b = int(GRADIENT_TOP[2] * (1 - ratio) + GRADIENT_BOTTOM[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def draw_circular_letter(self, x, y, letter, is_hovered=False, is_used=False, bounce_offset=0):
        """Draw a circular letter tile like in Text Twist with animation support"""
        # Apply bounce animation
        animated_y = y + bounce_offset

        # Choose colors based on state
        if is_used:
            circle_color = DARK_GRAY
            text_color = WHITE
        elif is_hovered:
            circle_color = LETTER_HOVER_COLOR
            text_color = BLACK
        else:
            circle_color = LETTER_CIRCLE_COLOR
            text_color = BLACK

        # Add glow effect for hovered letters
        if is_hovered:
            glow_radius = LETTER_CIRCLE_RADIUS + 5
            glow_color = (*LETTER_HOVER_COLOR[:3], 100)  # Semi-transparent
            pygame.draw.circle(self.screen, LETTER_HOVER_COLOR, (x, animated_y), glow_radius)

        # Draw circle with border
        pygame.draw.circle(self.screen, circle_color, (x, animated_y), LETTER_CIRCLE_RADIUS)
        pygame.draw.circle(self.screen, LETTER_CIRCLE_BORDER, (x, animated_y), LETTER_CIRCLE_RADIUS, 2)

        # Draw letter centered in circle
        text = self.font.render(letter, True, text_color)
        text_rect = text.get_rect(center=(x, animated_y))
        self.screen.blit(text, text_rect)
    
    def draw_letter_tiles(self):
        """Draw circular letter tiles in Text Twist style"""
        # Calculate positions for circular letters
        total_width = len(self.letters) * LETTER_SPACING
        start_x = (SCREEN_WIDTH - total_width) // 2 + LETTER_CIRCLE_RADIUS
        letter_y = 400  # Moved up to make room for buttons

        # Draw each letter as a circle
        for i, letter in enumerate(self.letters):
            x = start_x + i * LETTER_SPACING
            is_hovered = (i == self.hovered_letter)

            # Check if letter is used in current word
            used_count = self.current_word.count(letter)
            available_count = self.letters.count(letter)
            is_used = used_count >= available_count

            # Calculate bounce animation
            bounce_offset = 0
            if i in self.animations['letter_bounce']:
                bounce_time = self.animations['letter_bounce'][i]
                bounce_offset = -10 * math.sin(bounce_time * 10) * (bounce_time / 0.3)

            self.draw_circular_letter(x, letter_y, letter, is_hovered, is_used, bounce_offset)

    def draw_current_word_area(self):
        """Draw the current word input area with animations"""
        # Position it lower to make room for word grid
        word_bg_rect = pygame.Rect(150, 300, 500, CURRENT_WORD_HEIGHT)

        # Add flash effect for word submission
        bg_color = CURRENT_WORD_BG
        if self.animations['word_flash'] > 0:
            flash_intensity = self.animations['word_flash'] / 0.5
            bg_color = (
                min(255, CURRENT_WORD_BG[0] + int(100 * flash_intensity)),
                min(255, CURRENT_WORD_BG[1] + int(100 * flash_intensity)),
                min(255, CURRENT_WORD_BG[2] + int(100 * flash_intensity))
            )

        pygame.draw.rect(self.screen, bg_color, word_bg_rect)
        pygame.draw.rect(self.screen, WHITE, word_bg_rect, 3)

        # Draw current word with letter spacing and animations
        if self.current_word:
            letter_spacing = 30
            total_width = len(self.current_word) * letter_spacing
            start_x = SCREEN_WIDTH // 2 - total_width // 2

            for i, letter in enumerate(self.current_word):
                x = start_x + i * letter_spacing

                # Add typing animation (letters appear with a slight delay)
                alpha = min(255, (self.animation_time - i * 0.1) * 500)
                if alpha > 0:
                    text = self.font.render(letter, True, WHITE)
                    if alpha < 255:
                        text.set_alpha(alpha)
                    text_rect = text.get_rect(center=(x, 325))
                    self.screen.blit(text, text_rect)
        else:
            # Show placeholder text
            placeholder = self.small_font.render("Form words here...", True, WHITE)
            placeholder_rect = placeholder.get_rect(center=(SCREEN_WIDTH // 2, 325))
            self.screen.blit(placeholder, placeholder_rect)

    def draw_control_buttons(self):
        """Draw shuffle, clear, hint, and submit buttons"""
        button_y = 470  # Moved up to fit better
        button_width = 70

        # Shuffle button
        shuffle_rect = pygame.Rect(180, button_y, button_width, BUTTON_HEIGHT)
        self.shuffle_button_rect = shuffle_rect
        pygame.draw.rect(self.screen, BUTTON_COLOR, shuffle_rect)
        pygame.draw.rect(self.screen, WHITE, shuffle_rect, 2)
        shuffle_text = self.small_font.render("SHUFFLE", True, WHITE)
        shuffle_text_rect = shuffle_text.get_rect(center=shuffle_rect.center)
        self.screen.blit(shuffle_text, shuffle_text_rect)

        # Clear button
        clear_rect = pygame.Rect(270, button_y, button_width, BUTTON_HEIGHT)
        self.clear_button_rect = clear_rect
        pygame.draw.rect(self.screen, BUTTON_COLOR, clear_rect)
        pygame.draw.rect(self.screen, WHITE, clear_rect, 2)
        clear_text = self.small_font.render("CLEAR", True, WHITE)
        clear_text_rect = clear_text.get_rect(center=clear_rect.center)
        self.screen.blit(clear_text, clear_text_rect)

        # Hint button
        hint_rect = pygame.Rect(360, button_y, button_width, BUTTON_HEIGHT)
        self.hint_button_rect = hint_rect
        hint_color = BUTTON_COLOR if self.hints_available > 0 and not self.hint_used_this_round else DARK_GRAY
        pygame.draw.rect(self.screen, hint_color, hint_rect)
        pygame.draw.rect(self.screen, WHITE, hint_rect, 2)
        hint_text = self.small_font.render("HINT", True, WHITE)
        hint_text_rect = hint_text.get_rect(center=hint_rect.center)
        self.screen.blit(hint_text, hint_text_rect)

        # Submit button
        submit_rect = pygame.Rect(450, button_y, button_width, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, BUTTON_COLOR, submit_rect)
        pygame.draw.rect(self.screen, WHITE, submit_rect, 2)
        submit_text = self.small_font.render("SUBMIT", True, WHITE)
        submit_text_rect = submit_text.get_rect(center=submit_rect.center)
        self.screen.blit(submit_text, submit_text_rect)

    def draw_score_popups(self):
        """Draw animated score popups"""
        for text, x, y, time_left, base_alpha in self.animations['score_popup']:
            # Calculate animation properties
            progress = 1 - (time_left / 2.0)
            alpha = int(base_alpha * (1 - progress))
            offset_y = -50 * progress  # Float upward

            # Create text surface
            popup_text = self.font.render(text, True, (255, 255, 100))  # Yellow color
            popup_text.set_alpha(alpha)

            # Draw text
            text_rect = popup_text.get_rect(center=(x, y + offset_y))
            self.screen.blit(popup_text, text_rect)

    def draw_hint_message(self):
        """Draw the hint message if active"""
        if self.hint_display_time > 0 and self.hint_message:
            # Calculate fade effect
            alpha = min(255, int(self.hint_display_time * 255 / 2))

            # Create hint background
            hint_rect = pygame.Rect(100, 150, 600, 60)
            hint_bg = pygame.Surface((600, 60))
            hint_bg.set_alpha(200)
            hint_bg.fill((50, 50, 50))
            self.screen.blit(hint_bg, (100, 150))

            # Draw hint border
            pygame.draw.rect(self.screen, WHITE, hint_rect, 2)

            # Draw hint text
            hint_text = self.font.render(self.hint_message, True, WHITE)
            hint_text.set_alpha(alpha)
            hint_text_rect = hint_text.get_rect(center=hint_rect.center)
            self.screen.blit(hint_text, hint_text_rect)

    def draw_achievement_popup(self):
        """Draw achievement unlock popup"""
        if self.achievement_popup_time > 0 and self.achievement_popup:
            # Calculate slide-in animation
            progress = min(1.0, (4.0 - self.achievement_popup_time) / 0.5)
            slide_offset = int((1 - progress) * 300)

            # Achievement popup background
            popup_rect = pygame.Rect(SCREEN_WIDTH - 320 + slide_offset, 20, 300, 100)
            popup_bg = pygame.Surface((300, 100))
            popup_bg.set_alpha(240)
            popup_bg.fill((50, 100, 50))  # Green background
            self.screen.blit(popup_bg, popup_rect.topleft)

            # Draw popup border
            pygame.draw.rect(self.screen, (100, 200, 100), popup_rect, 3)

            # Achievement unlocked text
            unlock_text = self.small_font.render("ACHIEVEMENT UNLOCKED!", True, WHITE)
            unlock_rect = unlock_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.y + 10)
            self.screen.blit(unlock_text, unlock_rect)

            # Achievement name
            name_text = self.font.render(self.achievement_popup['name'], True, WHITE)
            name_rect = name_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.y + 35)
            self.screen.blit(name_text, name_rect)

            # Achievement description
            desc_text = self.small_font.render(self.achievement_popup['description'], True, WHITE)
            desc_rect = desc_text.get_rect(centerx=popup_rect.centerx, y=popup_rect.y + 65)
            self.screen.blit(desc_text, desc_rect)
    
    def draw_word_grid(self):
        """Draw word grid showing blanks for all possible words, filled in when found"""
        if not self.words_by_length:
            # Show placeholder text when no game is active
            placeholder = self.small_font.render("Start a game to see word blanks!", True, WHITE)
            self.screen.blit(placeholder, (50, 120))
            return

        # Draw word grid in the upper area
        start_x = 50
        start_y = 80  # Start below score/time/level info
        max_words_per_row = 8  # Adjust for better fit

        current_y = start_y
        for length in sorted(self.words_by_length.keys()):
            possible_words = self.words_by_length[length]

            # Draw length header with count
            found_count = len([w for w in possible_words if w in self.found_words])
            total_count = len(possible_words)
            length_text = self.small_font.render(f"{length} LETTERS ({found_count}/{total_count})", True, WHITE)

            # Add background for header
            header_rect = pygame.Rect(start_x - 5, current_y - 2, 180, 22)
            pygame.draw.rect(self.screen, BUTTON_COLOR, header_rect)
            pygame.draw.rect(self.screen, WHITE, header_rect, 1)
            self.screen.blit(length_text, (start_x, current_y))
            current_y += 30

            # Draw word slots in rows
            for i, possible_word in enumerate(possible_words):
                if i > 0 and i % max_words_per_row == 0:
                    current_y += WORD_GRID_CELL_HEIGHT + 3

                x = start_x + (i % max_words_per_row) * (WORD_GRID_CELL_WIDTH + 3)

                # Draw word slot background
                word_rect = pygame.Rect(x, current_y, WORD_GRID_CELL_WIDTH, WORD_GRID_CELL_HEIGHT)

                # Check if this word has been found
                if possible_word in self.found_words:
                    # Found word - show with green background
                    if possible_word == self.main_word:
                        # Main word gets special gold background
                        pygame.draw.rect(self.screen, (255, 215, 0), word_rect)  # Gold
                        pygame.draw.rect(self.screen, (255, 165, 0), word_rect, 3)  # Orange border
                    else:
                        pygame.draw.rect(self.screen, (100, 200, 100), word_rect)  # Light green
                        pygame.draw.rect(self.screen, (50, 150, 50), word_rect, 2)  # Dark green border

                    # Draw the actual word
                    word_text = self.small_font.render(possible_word.upper(), True, BLACK)
                    word_text_rect = word_text.get_rect(center=word_rect.center)
                    self.screen.blit(word_text, word_text_rect)
                else:
                    # Unfound word - show blanks
                    if possible_word == self.main_word:
                        # Main word slot gets special highlighting
                        pygame.draw.rect(self.screen, (255, 255, 200), word_rect)  # Light yellow
                        pygame.draw.rect(self.screen, (255, 215, 0), word_rect, 3)  # Gold border
                        blank_color = (200, 150, 0)  # Dark yellow for blanks
                    else:
                        pygame.draw.rect(self.screen, FOUND_WORD_BG, word_rect)
                        pygame.draw.rect(self.screen, DARK_GRAY, word_rect, 2)
                        blank_color = DARK_GRAY

                    # Draw blanks (underscores) for each letter
                    blanks = "_ " * length
                    blanks = blanks.strip()  # Remove trailing space
                    blank_text = self.small_font.render(blanks, True, blank_color)
                    blank_text_rect = blank_text.get_rect(center=word_rect.center)
                    self.screen.blit(blank_text, blank_text_rect)

            current_y += WORD_GRID_CELL_HEIGHT + 15  # Extra space between length groups

    def draw_game_screen(self):
        # Draw gradient background
        self.draw_gradient_background()

        # Draw score, level, and time with better styling
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))

        level_text = self.font.render(f"LEVEL: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (20, 50))

        # Show total words found vs total possible
        total_possible = len(self.all_possible_words)
        completion_percentage = int((len(self.found_words) / max(1, total_possible)) * 100)
        words_progress = self.font.render(f"WORDS: {len(self.found_words)}/{total_possible} ({completion_percentage}%)", True, WHITE)
        self.screen.blit(words_progress, (200, 20))

        # Show level advancement progress with main word requirement
        main_word_status = "✓" if self.found_main_word else "✗"
        main_word_color = (100, 255, 100) if self.found_main_word else (255, 100, 100)

        level_progress = self.font.render(f"GOAL: {len(self.found_words)}/{self.words_needed_to_advance} words", True, WHITE)
        self.screen.blit(level_progress, (200, 50))

        main_word_text = self.small_font.render(f"Main Word ({len(self.main_word)} letters): {main_word_status}", True, main_word_color)
        self.screen.blit(main_word_text, (200, 75))

        # Timer display with warning colors
        time_color = WHITE
        if self.timer_warning_active:
            # Flash red in last 10 seconds
            flash_intensity = (pygame.time.get_ticks() % 1000) / 1000.0
            if flash_intensity < 0.5:
                time_color = (255, 100, 100)  # Red
            else:
                time_color = (255, 255, 100)  # Yellow

        time_text = self.font.render(f"TIME: {int(self.time_left)}s", True, time_color)
        time_rect = time_text.get_rect()
        time_rect.topright = (SCREEN_WIDTH - 20, 20)
        self.screen.blit(time_text, time_rect)

        # Add warning message in last 10 seconds
        if self.timer_warning_active:
            warning_text = self.small_font.render("HURRY UP!", True, (255, 100, 100))
            warning_rect = warning_text.get_rect()
            warning_rect.topright = (SCREEN_WIDTH - 20, 45)
            self.screen.blit(warning_text, warning_rect)

        hints_text = self.font.render(f"HINTS: {self.hints_available}", True, WHITE)
        hints_rect = hints_text.get_rect()
        hints_rect.topright = (SCREEN_WIDTH - 20, 50)
        self.screen.blit(hints_text, hints_rect)

        # Draw all game elements
        self.draw_word_grid()
        self.draw_current_word_area()
        self.draw_letter_tiles()
        self.draw_control_buttons()
        self.draw_score_popups()
        self.draw_hint_message()
        self.draw_achievement_popup()
    
    def draw_menu_screen(self):
        # Draw gradient background
        self.draw_gradient_background()

        # Title with shadow effect
        title_shadow = self.big_font.render("WordCrafter", True, BLACK)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title_shadow.get_width()//2 + 3, 103))

        title = self.big_font.render("WordCrafter", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        subtitle = self.font.render("Text Twist Challenge", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 170))

        # Draw start button with modern styling
        start_rect = pygame.Rect(300, 300, 200, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, start_rect)
        pygame.draw.rect(self.screen, WHITE, start_rect, 3)
        start_text = self.font.render("START GAME", True, WHITE)
        start_text_rect = start_text.get_rect(center=start_rect.center)
        self.screen.blit(start_text, start_text_rect)

        # Draw instructions button
        instructions_rect = pygame.Rect(300, 380, 200, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, instructions_rect)
        pygame.draw.rect(self.screen, WHITE, instructions_rect, 3)
        instructions_text = self.font.render("HOW TO PLAY", True, WHITE)
        instructions_text_rect = instructions_text.get_rect(center=instructions_rect.center)
        self.screen.blit(instructions_text, instructions_text_rect)

        # Draw settings button
        settings_rect = pygame.Rect(300, 460, 200, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, settings_rect)
        pygame.draw.rect(self.screen, WHITE, settings_rect, 3)
        settings_text = self.font.render("SETTINGS", True, WHITE)
        settings_text_rect = settings_text.get_rect(center=settings_rect.center)
        self.screen.blit(settings_text, settings_text_rect)

        # Draw exit button
        exit_rect = pygame.Rect(300, 540, 200, 60)
        pygame.draw.rect(self.screen, DARK_GRAY, exit_rect)
        pygame.draw.rect(self.screen, WHITE, exit_rect, 3)
        exit_text = self.font.render("EXIT", True, WHITE)
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

    def draw_instructions_screen(self):
        # Draw gradient background
        self.draw_gradient_background()

        # Title
        title = self.big_font.render("HOW TO PLAY", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        # Instructions text
        instructions = [
            "OBJECTIVE:",
            "• Form words (3-7 letters) using the given letters",
            "• Find the main 6-letter word to advance levels",
            "• Find minimum required words per level",
            "• Longer words earn more points!",
            "",
            "CONTROLS:",
            "• Click letters or type on keyboard to form words",
            "• Press ENTER or click SUBMIT to submit a word",
            "• Press SPACE or click SHUFFLE to rearrange letters",
            "• Click CLEAR to clear current word",
            "• Press BACKSPACE to remove last letter",
            "• Press H for hints",
            "",
            "SCORING:",
            "• 3-letter: 100 pts, 4-letter: 400 pts",
            "• 5-letter: 800 pts, 6-letter: 1600 pts, 7-letter: 3200 pts",
            "• Time bonus: 10% per 10 seconds remaining",
            "• Main word bonus: +2000 pts",
            "• Completion bonus: +5000 pts for all words"
        ]

        y_offset = 120
        for line in instructions:
            if line.startswith("•"):
                text = self.small_font.render(line, True, WHITE)
                self.screen.blit(text, (100, y_offset))
            elif line == "":
                y_offset += 10
                continue
            else:
                text = self.font.render(line, True, WHITE)
                self.screen.blit(text, (50, y_offset))
            y_offset += 25

        # Back button
        back_rect = pygame.Rect(300, 520, 200, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, back_rect)
        pygame.draw.rect(self.screen, WHITE, back_rect, 3)
        back_text = self.font.render("BACK TO MENU", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

    def draw_settings_screen(self):
        # Draw gradient background
        self.draw_gradient_background()

        # Title
        title = self.big_font.render("SETTINGS", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        # Sound setting
        sound_text = self.font.render("SOUND:", True, WHITE)
        self.screen.blit(sound_text, (150, 150))

        sound_status = "ON" if self.settings['sound_enabled'] else "OFF"
        sound_color = BUTTON_COLOR if self.settings['sound_enabled'] else DARK_GRAY
        sound_rect = pygame.Rect(300, 140, 100, 40)
        pygame.draw.rect(self.screen, sound_color, sound_rect)
        pygame.draw.rect(self.screen, WHITE, sound_rect, 2)
        sound_status_text = self.small_font.render(sound_status, True, WHITE)
        sound_status_rect = sound_status_text.get_rect(center=sound_rect.center)
        self.screen.blit(sound_status_text, sound_status_rect)

        # Timer duration setting
        timer_text = self.font.render("TIMER:", True, WHITE)
        self.screen.blit(timer_text, (150, 220))

        timer_options = [120, 180, 240, 300]  # 2, 3, 4, 5 minutes
        for i, duration in enumerate(timer_options):
            x = 300 + i * 80
            timer_rect = pygame.Rect(x, 210, 70, 40)
            color = BUTTON_COLOR if self.settings['timer_duration'] == duration else DARK_GRAY
            pygame.draw.rect(self.screen, color, timer_rect)
            pygame.draw.rect(self.screen, WHITE, timer_rect, 2)
            timer_label = self.small_font.render(f"{duration//60}m", True, WHITE)
            timer_label_rect = timer_label.get_rect(center=timer_rect.center)
            self.screen.blit(timer_label, timer_label_rect)

        # Difficulty setting
        difficulty_text = self.font.render("DIFFICULTY:", True, WHITE)
        self.screen.blit(difficulty_text, (150, 290))

        difficulties = ['easy', 'normal', 'hard']
        for i, diff in enumerate(difficulties):
            x = 300 + i * 100
            diff_rect = pygame.Rect(x, 280, 90, 40)
            color = BUTTON_COLOR if self.settings['difficulty'] == diff else DARK_GRAY
            pygame.draw.rect(self.screen, color, diff_rect)
            pygame.draw.rect(self.screen, WHITE, diff_rect, 2)
            diff_label = self.small_font.render(diff.upper(), True, WHITE)
            diff_label_rect = diff_label.get_rect(center=diff_rect.center)
            self.screen.blit(diff_label, diff_label_rect)

        # Back button
        back_rect = pygame.Rect(300, 450, 200, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, back_rect)
        pygame.draw.rect(self.screen, WHITE, back_rect, 3)
        back_text = self.font.render("BACK TO MENU", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)

    def draw_level_complete_screen(self):
        # Draw gradient background
        self.draw_gradient_background()

        # Level Complete title with shadow
        level_complete_shadow = self.big_font.render("LEVEL COMPLETE!", True, BLACK)
        self.screen.blit(level_complete_shadow, (SCREEN_WIDTH//2 - level_complete_shadow.get_width()//2 + 3, 103))

        level_complete = self.big_font.render("LEVEL COMPLETE!", True, WHITE)
        self.screen.blit(level_complete, (SCREEN_WIDTH//2 - level_complete.get_width()//2, 100))

        # Level info
        level_text = self.font.render(f"LEVEL {self.current_level - 1} COMPLETED!", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 200))

        score_text = self.font.render(f"LEVEL SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 250))

        total_score_text = self.font.render(f"TOTAL SCORE: {self.total_score}", True, WHITE)
        self.screen.blit(total_score_text, (SCREEN_WIDTH//2 - total_score_text.get_width()//2, 300))

        # Next level info
        next_level_text = self.font.render(f"NEXT: LEVEL {self.current_level}", True, WHITE)
        self.screen.blit(next_level_text, (SCREEN_WIDTH//2 - next_level_text.get_width()//2, 350))

        # Continue button
        continue_rect = pygame.Rect(300, 420, 200, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, continue_rect)
        pygame.draw.rect(self.screen, WHITE, continue_rect, 3)
        continue_text = self.font.render("CONTINUE", True, WHITE)
        continue_text_rect = continue_text.get_rect(center=continue_rect.center)
        self.screen.blit(continue_text, continue_text_rect)

        # Menu button
        menu_rect = pygame.Rect(300, 500, 200, 60)
        pygame.draw.rect(self.screen, DARK_GRAY, menu_rect)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 3)
        menu_text = self.font.render("MAIN MENU", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)

    def draw_game_over_screen(self):
        # Draw gradient background
        self.draw_gradient_background()

        # Game Over title with shadow
        game_over_shadow = self.big_font.render("GAME OVER!", True, BLACK)
        self.screen.blit(game_over_shadow, (SCREEN_WIDTH//2 - game_over_shadow.get_width()//2 + 3, 103))

        game_over = self.big_font.render("GAME OVER!", True, WHITE)
        self.screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 100))

        # Score display
        score_text = self.font.render(f"FINAL SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 200))

        # Game statistics
        words_found = self.font.render(f"WORDS FOUND: {len(self.found_words)}/{len(self.all_possible_words)}", True, WHITE)
        self.screen.blit(words_found, (SCREEN_WIDTH//2 - words_found.get_width()//2, 230))

        level_reached = self.font.render(f"LEVEL REACHED: {self.current_level}", True, WHITE)
        self.screen.blit(level_reached, (SCREEN_WIDTH//2 - level_reached.get_width()//2, 260))

        main_word_status = "YES" if self.found_main_word else "NO"
        main_word_color = (100, 255, 100) if self.found_main_word else (255, 100, 100)
        main_word_text = self.font.render(f"MAIN WORD FOUND: {main_word_status}", True, main_word_color)
        self.screen.blit(main_word_text, (SCREEN_WIDTH//2 - main_word_text.get_width()//2, 290))

        # Draw play again button
        again_rect = pygame.Rect(300, 350, 200, 60)
        pygame.draw.rect(self.screen, BUTTON_COLOR, again_rect)
        pygame.draw.rect(self.screen, WHITE, again_rect, 3)
        again_text = self.font.render("PLAY AGAIN", True, WHITE)
        again_text_rect = again_text.get_rect(center=again_rect.center)
        self.screen.blit(again_text, again_text_rect)

        # Draw menu button
        menu_rect = pygame.Rect(300, 430, 200, 60)
        pygame.draw.rect(self.screen, DARK_GRAY, menu_rect)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 3)
        menu_text = self.font.render("MAIN MENU", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
    
    def get_letter_at_mouse(self, mouse_pos):
        """Check if mouse is over a letter circle"""
        total_width = len(self.letters) * LETTER_SPACING
        start_x = (SCREEN_WIDTH - total_width) // 2 + LETTER_CIRCLE_RADIUS
        letter_y = 400  # Updated to match new position

        for i, letter in enumerate(self.letters):
            x = start_x + i * LETTER_SPACING
            distance = ((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - letter_y) ** 2) ** 0.5
            if distance <= LETTER_CIRCLE_RADIUS:
                return i, letter
        return None, None

    async def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        # Update hover state for letters
        if self.current_state == GAME_STATE:
            letter_index, _ = self.get_letter_at_mouse(mouse_pos)
            self.hovered_letter = letter_index if letter_index is not None else -1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.current_state == GAME_STATE:
                    if event.key == pygame.K_BACKSPACE:
                        self.remove_last_letter()
                    elif event.key == pygame.K_RETURN:
                        self.submit_word()
                    elif event.key == pygame.K_SPACE:
                        self.shuffle_letters()
                    elif event.key == pygame.K_h:
                        self.use_hint()
                    elif event.unicode.isalpha():
                        self.add_letter(event.unicode.upper())
                elif event.key == pygame.K_ESCAPE:
                    # ESC key returns to menu from any screen
                    self.current_state = MENU_STATE

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.current_state == MENU_STATE:
                    # Menu screen - check button clicks
                    start_rect = pygame.Rect(300, 300, 200, 60)
                    instructions_rect = pygame.Rect(300, 380, 200, 60)
                    settings_rect = pygame.Rect(300, 460, 200, 60)
                    exit_rect = pygame.Rect(300, 540, 200, 60)

                    if start_rect.collidepoint(mouse_pos):
                        self.start_new_game()
                    elif instructions_rect.collidepoint(mouse_pos):
                        self.start_screen_transition()
                        self.current_state = INSTRUCTIONS_STATE
                    elif settings_rect.collidepoint(mouse_pos):
                        self.start_screen_transition()
                        self.current_state = SETTINGS_STATE
                    elif exit_rect.collidepoint(mouse_pos):
                        self.running = False

                elif self.current_state == INSTRUCTIONS_STATE:
                    # Instructions screen - check back button
                    back_rect = pygame.Rect(300, 520, 200, 60)
                    if back_rect.collidepoint(mouse_pos):
                        self.current_state = MENU_STATE

                elif self.current_state == SETTINGS_STATE:
                    # Settings screen - check all setting buttons
                    # Sound toggle
                    sound_rect = pygame.Rect(300, 140, 100, 40)
                    if sound_rect.collidepoint(mouse_pos):
                        self.settings['sound_enabled'] = not self.settings['sound_enabled']
                        self.sound_manager.set_enabled(self.settings['sound_enabled'])

                    # Timer duration buttons
                    timer_options = [120, 180, 240, 300]
                    for i, duration in enumerate(timer_options):
                        x = 300 + i * 80
                        timer_rect = pygame.Rect(x, 210, 70, 40)
                        if timer_rect.collidepoint(mouse_pos):
                            self.settings['timer_duration'] = duration

                    # Difficulty buttons
                    difficulties = ['easy', 'normal', 'hard']
                    for i, diff in enumerate(difficulties):
                        x = 300 + i * 100
                        diff_rect = pygame.Rect(x, 280, 90, 40)
                        if diff_rect.collidepoint(mouse_pos):
                            self.settings['difficulty'] = diff

                    # Back button
                    back_rect = pygame.Rect(300, 450, 200, 60)
                    if back_rect.collidepoint(mouse_pos):
                        self.current_state = MENU_STATE

                elif self.current_state == GAME_STATE:
                    # Game screen - check letter clicks and button clicks
                    letter_index, letter = self.get_letter_at_mouse(mouse_pos)
                    if letter_index is not None:
                        self.add_letter(letter)

                    # Check control buttons
                    if self.shuffle_button_rect and self.shuffle_button_rect.collidepoint(mouse_pos):
                        self.shuffle_letters()
                    elif self.clear_button_rect and self.clear_button_rect.collidepoint(mouse_pos):
                        self.clear_current_word()
                    elif self.hint_button_rect and self.hint_button_rect.collidepoint(mouse_pos):
                        self.use_hint()
                    else:
                        # Check submit button
                        submit_rect = pygame.Rect(450, 470, 70, BUTTON_HEIGHT)  # Updated position
                        if submit_rect.collidepoint(mouse_pos):
                            self.submit_word()

                elif self.current_state == LEVEL_COMPLETE_STATE:
                    # Level complete screen - check button clicks
                    continue_rect = pygame.Rect(300, 420, 200, 60)
                    menu_rect = pygame.Rect(300, 500, 200, 60)

                    if continue_rect.collidepoint(mouse_pos):
                        self.start_new_game()  # Continue to next level
                    elif menu_rect.collidepoint(mouse_pos):
                        self.current_state = MENU_STATE

                elif self.current_state == GAME_OVER_STATE:
                    # Game over screen - check button clicks
                    again_rect = pygame.Rect(300, 350, 200, 60)
                    menu_rect = pygame.Rect(300, 430, 200, 60)

                    if again_rect.collidepoint(mouse_pos):
                        self.start_new_game()
                    elif menu_rect.collidepoint(mouse_pos):
                        self.current_state = MENU_STATE
    
    async def run(self):
        await self.initialize()
        last_time = pygame.time.get_ticks()

        while self.running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Delta time in seconds
            last_time = current_time

            await self.handle_events()

            # Update animations
            self.update_animations(dt)

            if self.current_state == GAME_STATE:
                self.update_time()
                self.draw_game_screen()
            elif self.current_state == LEVEL_COMPLETE_STATE:
                self.draw_level_complete_screen()
            elif self.current_state == GAME_OVER_STATE:
                self.draw_game_over_screen()
            elif self.current_state == INSTRUCTIONS_STATE:
                self.draw_instructions_screen()
            elif self.current_state == SETTINGS_STATE:
                self.draw_settings_screen()
            else:  # MENU_STATE
                self.draw_menu_screen()

            pygame.display.flip()
            self.clock.tick(60)
            await asyncio.sleep(0)  # Yield control to the browser

async def main():
    game = WordCrafter()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())