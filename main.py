import time
import tkinter as tk
import string
from tkinter import ttk, scrolledtext, messagebox


def print_suggested_words(suggested_words, time_spent):
    result = ""
    for key in suggested_words.keys():
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
    for word in current_words_dict.keys():
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
    for word in wrong_dict.keys():
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
    for word in set(text_list):
        i = 0
        for index, letter in enumerate(word):
            if letter in dictionary.keys():
                if index == len(word) - 1:
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
    punctuation = string.punctuation
    for word in text.split(" "):
        cleaned_word = ''.join(char for char in word if char not in punctuation)
        if cleaned_word.isalpha():
            word_list.append(cleaned_word)
    return word_list


def add_word(word, tree):
    current_dict = tree
    for index, letter in enumerate(word):
        if letter not in current_dict.keys():
            current_dict[letter] = {}
        if index == len(word) - 1:
            if "$" in current_dict.keys():
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
        self.root.geometry('600x500')
        self.language = tk.StringVar()
        self.text_input = tk.StringVar()
        self.path = None
        self.create_main_window()

    def create_main_window(self):
        tk.Label(self.root, text="Select Language :").place(x=10, y=50)
        language_combobox = ttk.Combobox(self.root, textvariable=self.language,
                                         values=["English", "فارسی"], width=10, height=5)
        language_combobox.place(x=130, y=53)
        ttk.Label(self.root, text="Enter Text:").place(x=40, y=100)
        self.text_input = tk.Text(self.root, width=60, height=17)
        self.text_input.place(x=40 , y=130)
        ttk.Button(self.root, text="Check Spelling", command=self.check_spelling).place(x=300, y=440)
        ttk.Button(self.root, text='Exit', command=self.exit).place(x=100, y=440)

    def set_language(self):
        if not self.language.get() :
            messagebox.showwarning("Warning", "Please select a language")
            return False
        else:
            if self.language.get() == "فارسی":
                self.path = "dictionary_fa.txt"
            elif self.language.get() == "English":
                self.path = "dictionary.txt"
            return True

    def exit(self):
        self.root.quit()

    def check_spelling(self):
        if self.set_language():
            paragraph = self.text_input.get('1.0', tk.END).strip()
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
            self.next()
            self.show_results(paragraph, wrong_dict, result)

    def show_results(self, paragraph, wrong_words, result):
        self.root.config(bd=10)
        result_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=25)
        result_area.pack(pady=20)
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

    def next(self):
        for widget in self.root.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    SpellCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
