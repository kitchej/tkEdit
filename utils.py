import tkinter as tk


def get_first_string_index(string, text_widget, regex=False, no_case=False, start="1.0"):
    """
    A helper function that finds the start and end index of the FIRST instance of a string within a text widget
    """
    length = tk.IntVar()
    word_start = text_widget.search(string, start, regexp=regex, stopindex=tk.END, nocase=no_case, count=length)
    if word_start == '':
        return None
    word_start_index = word_start.split(".")
    start_row = int(word_start_index[0])
    start_column = int(word_start_index[1])
    end_row = start_row + string.count('\n')
    end_column = start_column + length.get()
    word_end = f"{end_row}.{end_column}"
    return word_start, word_end


def get_string_indexes(string, text_widget, regex=False, no_case=False, start="1.0"):
    """
    A helper function that finds the start and end indexes of ALL instances of a string within a text widget
    """
    length = tk.IntVar()
    out = []
    while start != text_widget.index(tk.END):
        word_start = text_widget.search(string, start, regexp=regex, stopindex=tk.END, nocase=no_case, count=length)
        if word_start == '':
            break
        word_start_index = word_start.split(".")
        start_row = int(word_start_index[0])
        start_column = int(word_start_index[1])
        end_row = start_row + string.count('\n')
        end_column = start_column + length.get()
        word_end = f"{end_row}.{end_column}"
        start = word_end
        out.append((word_start, word_end))
    return out

def get_tags(start, end, text_obj):
    """
    Provided by Bryan Oakley
    https://stackoverflow.com/questions/61661490/how-do-you-get-the-tags-from-text-in-a-tkinter-text-widget
    """
    index = start
    tags = []
    while text_obj.compare(index, "<=", end):
        tags.extend((text_obj.tag_names(index)))
        index = text_obj.index(f"{index}+1c")
    return set(tags)
