import tkinter as tk
from tkinter import ttk
import sys
from os import close
import pyperclip
import ChapterVerse
import list_and_str_ops as list
from BibleFileNames import files
from charEliminator import onlyVerses, remove_only_chars
from tkinter.ttk import *
from tkinter import *

window = tk.Tk()
window.title("Desktop Bible")

toolbar_frame = tk.Frame(window)
toolbar_frame.rowconfigure([0,1], weight=1)
toolbar_frame.columnconfigure([0, 1, 2, 3, 4, 5, 6,7,8], weight=1, minsize=45)
toolbar_frame.pack(fill=tk.X)

books_titled = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","First Samuel","Second Samuel","First Kings","Second Kings","First Chronicles","Second Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Eccliasiastes","Song Of Solomon","Isaiah","Jeremiah","Lamentations","Ezekial","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi","Matthew","Mark","Luke","John","Acts","Romans","First Corinthians","Second Corinthians","Galatians","Ephesians","Philipians","Colossians","First Thesselonians","Second Thesselonians","First Timothy","Second Timothy","Titus","Philemon","Hebrews","James","First Peter","Second Peter","First John","Second John","Third John","Jude","Revelation"]
books_file_names = ["genesis.txt", "exodus.txt", "leviticus.txt", "numbers.txt", "deuteronomy.txt", "joshua.txt", "judges.txt", "ruth.txt", "first_samuel.txt", "second_samuel.txt", "first_kings.txt", "second_kings.txt", "first_chronicles.txt", "second_chronicles.txt", "ezra.txt", "nehemiah.txt", "esther.txt", "job.txt", "psalms.txt", "proverbs.txt", "eccliasiastes.txt", "song_of_solomon.txt", "isaiah.txt", "jeremiah.txt", "lamentations.txt", "ezekial.txt", "daniel.txt", "hosea.txt", "joel.txt", "amos.txt", "obadiah.txt", "jonah.txt", "micah.txt", "nahum.txt", "habakkuk.txt", "zephaniah.txt", "haggai.txt", "zechariah.txt", "malachi.txt", "matthew.txt", "mark.txt", "luke.txt", "john.txt", "acts.txt", "romans.txt", "first_corinthians.txt", "second_corinthians.txt", "galatians.txt", "ephesians.txt", "philipians.txt", "colossians.txt", "first_thesselonians.txt", "second_thesselonians.txt", "first_timothy.txt", "second_timothy.txt", "titus.txt", "philemon.txt", "hebrews.txt", "james.txt", "first_peter.txt", "second_peter.txt", "first_john.txt", "second_john.txt", "third_john.txt", "jude.txt", "revelation.txt"]

bible_text_widget_frame = tk.Frame(window)
bible_text_widget_frame.pack(fill=tk.BOTH,expand=True)

def search_button_event():
  print("search button was clicked")
  search_word = f"{searchBar_entry.get()}"
  if(hasonlyspaces(search_word)):
    return
  else:
    linearsearch(search_word)

def search_entry_enter(event):
  search_button_event()

def clear_text_field():
  print("clearing text field")
  searchBar_entry.delete(0,END)

def go_home():
  txt = open("Bible.txt","r")
  update_bible_text_widget(txt.read())
  txt.close()

searchBar_label = tk.Label(
    master=toolbar_frame,
    text="Enter search characters:"
)
searchBar_entry = tk.Entry(
    master=toolbar_frame
)
searchBar_entry.bind("<Return>",search_entry_enter)
clear_button = tk.Button(
    master=toolbar_frame,
    text="Clear",
    command=clear_text_field
)
home_button = tk.Button(
    master=toolbar_frame,
    text="Home",
    command=go_home
)
search_button = tk.Button(
    master=toolbar_frame,
    text="Search",
    command=search_button_event
)
number_of_results_label = tk.Label(
    master=toolbar_frame,
    text="No search results yet..."
)

value_inside_book_selector = tk.StringVar(toolbar_frame)
# Set the default value of the variable
value_inside_book_selector.set("Select an Book")

value_inside_chapter_selecter = tk.StringVar(toolbar_frame)
value_inside_chapter_selecter.set("")

value_inside_verse_selecter = tk.StringVar(toolbar_frame)
value_inside_verse_selecter.set("")

def get_selected_book_from_dropdown():
  book = book_selector_combobox.get()
  book_file_name = books_file_names[books_titled.index(book)]
  return book_file_name

def get_selected_chapter_from_dropdown():
  chapter = chapter_selector_combobox.get()
  return int(chapter)
'''--------------------------------------------------'''

book_selector_combobox = ttk.Combobox(
    toolbar_frame,
    width=18,
    textvariable=value_inside_book_selector
)
def get_selected_book(event):
  SELECTED_BOOK = get_selected_book_from_dropdown()
  print(SELECTED_BOOK)
  file = open(SELECTED_BOOK,"r")
  update_bible_text_widget(file.read())
  file.close()

  file_for_list = open(SELECTED_BOOK,"r")
  file_list = file_for_list.readlines()
  number_of_chapters = int(file_list[-1].split(':')[0])+1
  new_combobox_values = []
  for i in range(number_of_chapters):
    new_combobox_values.append(str(i))
  chapter_selector_combobox['values'] = new_combobox_values

  file_for_list.close()

book_selector_combobox.bind("<<ComboboxSelected>>",get_selected_book)
book_selector_combobox['values'] = books_titled

'''--------------------------------------------------'''
chapter_selector_combobox = ttk.Combobox(
   toolbar_frame,
   width=4,
   textvariable=value_inside_chapter_selecter
)
chapter_selector_combobox['values'] = []
def get_selected_chapter(event):
  chapter_list = ChapterVerse.get_chap(get_selected_book_from_dropdown(), get_selected_chapter_from_dropdown())
  chapter_text = " ".join(chapter_list)
  number_of_verses_in_chapter = 0
  numbers_for_verse_dropdown = []
  for chapter in chapter_list:
    number_of_verses_in_chapter += 1
    numbers_for_verse_dropdown.append(str(number_of_verses_in_chapter))

  verse_selector_combobox['values'] = numbers_for_verse_dropdown

  update_bible_text_widget(chapter_text)

chapter_selector_combobox.bind("<<ComboboxSelected>>",get_selected_chapter)


'''--------------------------------------------------'''

verse_selector_combobox = ttk.Combobox(
  toolbar_frame,
  width=4,
  textvariable=value_inside_verse_selecter
)
verse_selector_combobox['values'] = []

def get_selected_verse(event):
  verse = verse_selector_combobox.get()
  verse_text = ChapterVerse.get_verse(get_selected_book_from_dropdown(),get_selected_chapter_from_dropdown(),int(verse))
  update_bible_text_widget(verse_text)
  print(verse)
verse_selector_combobox.bind("<<ComboboxSelected>>",get_selected_verse)

'''------------------------------------------------'''


bible_text_widget = tk.Text(
  master=bible_text_widget_frame,
  wrap=tk.WORD
)

# Grid layout configuration
searchBar_label.grid(row=0, column=0, sticky="ew")
searchBar_entry.grid(row=0, column=1, sticky="ew")
clear_button.grid(row=0, column=2, sticky="ew")
home_button.grid(row=0, column=3, sticky="ew")
search_button.grid(row=0, column=4, sticky="ew")
number_of_results_label.grid(row=0, column=5, sticky="ew")
book_selector_combobox.grid(row=0, column=6, sticky="ew")
chapter_selector_combobox.grid(row=0,column=7,sticky="ew")
verse_selector_combobox.grid(row=0,column=8,sticky="ew")

bible_text_widget.pack(fill=tk.BOTH,expand=True)

bible_text_widget.config(state=DISABLED)  #state must be disable so the user cant edit the bible text

multiple_results = []
file = open('bibleSearchResult.txt','w')
file.write('')
#clearing results so next results don't have previous results mixed in
file.close()



def update_bible_text_widget(text):
  bible_text_widget.config(state=NORMAL)
  bible_text_widget.delete("1.0","end")
  bible_text_widget.insert(tk.END,text)
  bible_text_widget.config(state=DISABLED)

def setsearchrange(startbook,endbook,listoffiles):
  indexoffirstbook = listoffiles.index(f'{list.disclean(startbook)}')
  indexofendbook = listoffiles.index(f'{list.disclean(endbook)}')
  files = listoffiles[indexoffirstbook:indexofendbook+1]
  return files

bible_text_home = open("Bible.txt","r")
update_bible_text_widget(bible_text_home.read())
bible_text_home.close()

def linearsearch(searchkey):
  #argument should be search_input
  '''This is the initial search engine for the BibleApp.\n
  It takes a string as input and ouputs to the tkinter window
  '''
  for book in files:
    verses = open(book).readlines()
    book = clean(book)
    for verse in verses:
      if searchkey.lower() in verse.lower(): 
        multiple_results.append(f"{book}\n{verse}")
  for result in multiple_results:
    open("bibleSearchResult.txt",'a').write(f'{result}')

  bible_text_widget_text = f"{open('bibleSearchResult.txt').read()}"
  update_bible_text_widget(bible_text_widget_text)

  if len(multiple_results) == 0:
    number_of_results_label.config(text="")
    number_of_results_label.config(text=f"no results found for '{searchkey}'")

    update_bible_text_widget("Sorry, the keywords you searched for are not in the Bible. Try searching the same keyword(s) with different spacing or punctuation.(The search is not case sensitive.)")
  elif len(multiple_results) == 1:        
    number_of_results_label.config(text="")
    number_of_results_label.config(text=f"{len(multiple_results)} result found for '{searchkey}'")
  else:  
    number_of_results_label.config(text="")
    number_of_results_label.config(text=f"{len(multiple_results)} results found for '{searchkey}'")

def clean(str):
  '''This function is similar to the clean() function in list_and_str_ops module except that it uses .title() instead of .lower()'''
  str = str.replace("_", " ")
  halves = str.split(".")
  return str.replace(str, halves[0].title())

def hasonlyspaces(string):
  '''hasonlyspaces() is a function that returns True if the string it recieves as input consists of only spaces and returns False otherwise.'''
  spaces = []
  for character in string:
    if character == " ":
      spaces.append(character)
  if len(spaces) == len(string):
    return True
  else:
    return False
  
window.mainloop()