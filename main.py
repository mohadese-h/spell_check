
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


def print_suggested_words(suggested_words, time_spent):
    result = ""
    for key in list(suggested_words.keys()):
        result += key + " :"
        for word in suggested_words[key]:
            result += word
            if word != suggested_words[key][len(suggested_words[key]) - 1]:
                result += ", "
            else:
                result += "\n"
    result += f"\nTime spent: {time_spent} seconds"
    return result


def edit_distance(word, correct_word):
    memo = {}

    def dp(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        if i == 0:
            return j
        if j == 0:
            return i
        if word[i - 1] == correct_word[j - 1]:
            result = dp(i - 1, j - 1)
        else:
            result = 1 + min(dp(i - 1, j), dp(i, j - 1), dp(i - 1, j - 1))
        memo[(i, j)] = result
        return result

    return dp(len(word), len(correct_word))


def find_suggested_words(current_words_dict):
    suggested_words = {}
    wrong_words_list = list(current_words_dict.keys())
    for word in wrong_words_list:
        current_list = current_words_dict[word]
        suggested_dict = {}
        i = 1
        for current_word in current_list:
            difference = edit_distance(word, current_word)
            if i > 3:
                x, y, z = list(suggested_dict.values())
                maxi = max(x, y, z, difference)
                if maxi != difference:
                    for key in list(suggested_dict.keys()):
                        if maxi == suggested_dict[key]:
                            suggested_dict.pop(key)
                            suggested_dict[current_word] = difference
                            break
            else:
                suggested_dict[current_word] = difference
                i += 1
        suggested_words[word] = list(suggested_dict.keys())
    return suggested_words


def find_current_words(wrong_dict, path):
    current_words_dict = {}
    wrong_words_list = list(wrong_dict.keys())
    for word in wrong_words_list:
        current_words_dict[word] = []
        current_section_start = word[0: wrong_dict[word]]
        current_section_end = word[1:]
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip().startswith(current_section_start) or line.strip().endswith(current_section_end) \
                        or line.strip().__contains__(current_section_end):
                    current_words_dict[word].append(line.strip())
    return current_words_dict


def find_wrong_word(text_list, tree):
    wrong_dict = {}
    dictionary = tree
    text_list = list(set(text_list))
    for word in text_list:
        i = 0
        letter_list = list(word)
        for index, letter in enumerate(letter_list):
            if letter in list(dictionary.keys()):
                if index == len(letter_list) - 1:
                    if "$" in list(dictionary.keys()):
                        if letter not in dictionary["$"]:
                            wrong_dict[word] = i
                            break
                dictionary = dictionary[letter]
                i += 1
            else:
                wrong_dict[word] = i
                break
        dictionary = tree
    return wrong_dict


def text_to_list(text):
    text = text.lower()
    word_list = []
    punctuation = '''!()-[]{};:'"\\,<>./?@#$%^&*_~'''
    for word in text.split(" "):
        cleaned_word = ''.join(char for char in word if char not in punctuation)
        if cleaned_word.isalpha():
            word_list.append(cleaned_word)
    return word_list


def add_word(word, tree):
    letter_list = list(word)
    current_dict = tree
    for index, letter in enumerate(letter_list):
        if letter not in list(current_dict.keys()):
            current_dict[letter] = {}
        if index == len(letter_list) - 1:
            if "$" in list(current_dict.keys()):
                if letter not in current_dict["$"]:
                    current_dict["$"].append(letter)
            else:
                current_dict["$"] = []
                current_dict["$"].append(letter)
        current_dict = current_dict[letter]


def upload_dictionary(tree, path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            add_word(line.strip(), tree)
    return tree


class SpellCheckerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Spell Checker")
        self.center = self.center_window(900, 600)
        self.root.geometry(self.center)
        self.language = tk.StringVar()
        self.text_input = tk.StringVar()
        self.notebook = ttk.Notebook(self.root)
        self.language_frame = ttk.Frame(self.notebook)
        self.text_frame = ttk.Frame(self.notebook)
        self.text_area = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, width=100, height=25)
        self.path = None
        self.create_main_window()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        return f'{width}x{height}+{x}+{y}'

    def create_main_window(self):
        self.notebook.pack(padx=10, pady=10)
        self.notebook.add(self.language_frame, text='Language Selection')
        self.notebook.add(self.text_frame, text='Text Input')
        self.create_language_selection()
        self.create_text_input()

    def create_language_selection(self):
        ttk.Label(self.language_frame, text="Select Language:").pack(pady=10)
        language_combobox = ttk.Combobox(self.language_frame, textvariable=self.language, values=["English", "فارسی"])
        language_combobox.pack(pady=5)
        ttk.Button(self.language_frame, text="Next", command=self.set_language).pack(pady=20)

    def set_language(self):
        if self.language.get() == "فارسی":
            self.path = "dictionary_fa.txt"
        else:
            self.path = "dictionary.txt"
        self.notebook.select(self.text_frame)

    def create_text_input(self):
        ttk.Label(self.text_frame, text="Enter Text:").pack(pady=10)
        self.text_area.pack(pady=10)
        ttk.Button(self.text_frame, text="Check Spelling", command=self.check_spelling).pack(pady=20)

    def check_spelling(self):
        paragraph = self.text_area.get("1.0", tk.END).strip()
        if not paragraph:
            messagebox.showwarning("Warning", "Please enter some text.")
            return

        start_time = time.time()
        tree = upload_dictionary({}, self.path)
        tex_list = text_to_list(paragraph)
        wrong_dict = find_wrong_word(tex_list, tree)
        current_words = find_current_words(wrong_dict, self.path)
        suggested_words = find_suggested_words(current_words)
        end_time = time.time()
        time_spent = end_time - start_time
        result = print_suggested_words(suggested_words, time_spent)
        self.show_results(paragraph, wrong_dict, result)

    def show_results(self, paragraph, wrong_words, result):
        result_window = tk.Toplevel(self.root)
        result_window.title("Results")
        result_window.geometry(self.center)
        frame = ttk.Frame(result_window)
        frame.pack(pady=10, padx=10)
        result_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=30)
        result_area.pack(pady=10, padx=10)
        result_area.tag_config('error', foreground='red')
        words = paragraph.split()
        for word in words:
            if word.lower() in wrong_words:
                result_area.insert(tk.END, word + " ", 'error')
            else:
                result_area.insert(tk.END, word + " ")
        result_area.insert(tk.END, "\n\nSuggestions:\n")
        result_area.insert(tk.END, result)
        result_area.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    SpellCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
