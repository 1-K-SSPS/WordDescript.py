import random
import re
import unicodedata
import os
import sys
import curses
import signal

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

def calculate_precision(input_word, correct_word):
    input_words = normalize_string(input_word).split()
    correct_words = normalize_string(correct_word).split()
    
    matches = sum(1 for word in input_words if word in correct_words)
    total_words = len(correct_words)
    
    return (matches / total_words) * 100 if total_words > 0 else 0

def get_precision_message(precision):
    if precision <= 25:
        return "Jsi uvařenej bro"
    elif precision <= 50:
        return "meh..."
    elif precision <= 75:
        return "lowkey vaříš"
    else:
        return "Navařils frfr"

def load_definitions_from_file(file_path):
    definitions = {}
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read().strip()
            pairs = re.split(r'\s*,\s*|\s*;\s*|\s*\n\s*', content)
            for pair in pairs:
                if '-' in pair:
                    word, description = pair.split('-', 1)
                    definitions[word.strip()] = description.strip()
    except Exception as e:
        print(f"Chyba při načítání souboru: {e}")
    return definitions

def update_stats(stdscr, total_precision, total_questions):
    height, width = stdscr.getmaxyx()
    avg_precision = total_precision / total_questions if total_questions > 0 else 0
    stats = f"Přesnost: {avg_precision:.2f}% | Otázky: {total_questions}"
    stdscr.addstr(height - 1, width - len(stats) - 1, stats)
    stdscr.refresh()

def handle_interrupt(signum, frame):
    raise KeyboardInterrupt

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    
    signal.signal(signal.SIGINT, handle_interrupt)
    
    definitions = {}
    total_precision = 0
    total_questions = 0
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        definitions = load_definitions_from_file(file_path)
    
    if not definitions:
        stdscr.addstr(0, 0, "Použítí: Learnthon.py [cesta_k_souboru] (formát: slovo - definice, slovo - definice, ...)")
        stdscr.refresh()
        stdscr.getch()
        return
    
    all_words = list(definitions.keys())
    random.shuffle(all_words)
    
    try:
        for random_word in all_words:
            stdscr.clear()
            random_description = definitions[random_word]
            quiz_type = random.choice(["word", "description"])
            
            if quiz_type == "word":
                question = f"\nDefinice: {random_description}"
                stdscr.addstr(0, 0, question)
                stdscr.addstr(2, 0, "Jaké slovo odpovídá této definici? ")
                correct_answer = random_word
            else:
                question = f"\nSlovo: {random_word}"
                stdscr.addstr(0, 0, question)
                stdscr.addstr(2, 0, "Jaká je definice tohoto slova? ")
                correct_answer = random_description
            
            update_stats(stdscr, total_precision, total_questions)
            stdscr.refresh()
            
            curses.echo()
            user_answer = stdscr.getstr(2, len("Jaké slovo odpovídá této definici? ")).decode('utf-8', errors='replace')
            curses.noecho()
            
            if user_answer.lower() == 'q':
                break
            
            precision = calculate_precision(user_answer, correct_answer)
            total_precision += precision
            total_questions += 1
            
            stdscr.clear()
            stdscr.addstr(0, 0, question)
            stdscr.addstr(2, 0, f"Přesnost (odhadovaná, neberte moc vážně): {precision:.2f}%")
            stdscr.addstr(3, 0, f"Správná odpověď: {correct_answer}")
            stdscr.addstr(4, 0, f"Vaše odpověď: {user_answer}")
            stdscr.addstr(6, 0, "Stiskněte Enter pro další otázku (nebo 'q' pro ukončení)...")
            
            update_stats(stdscr, total_precision, total_questions)
            stdscr.refresh()
            
            user_input = stdscr.getch()
            if user_input == ord('q'):
                break
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        stdscr.addstr(8, 0, f"Došlo k chybě: {e}. Tvůj progress byl uložen. Pokračujeme...")
        stdscr.addstr(9, 0, "Stiskněte Enter pro pokračování...")
        stdscr.refresh()
        stdscr.getch()
    
    stdscr.clear()
    if total_questions > 0:
        average_precision = total_precision / total_questions
        stdscr.addstr(0, 0, "\nUkončeno!")
        stdscr.addstr(2, 0, f"Celkový počet zodpovězených otázek: {total_questions}")
        stdscr.addstr(3, 0, f"Průměrná přesnost (odhadovaná, neberte moc vážně): {average_precision:.2f}%")
        stdscr.addstr(4, 0, get_precision_message(average_precision))
    else:
        stdscr.addstr(0, 0, "\nNebyly zodpovězeny žádné otázky.")
    
    update_stats(stdscr, total_precision, total_questions)
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
