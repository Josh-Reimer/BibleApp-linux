'''
DO NOT DELETE!
THIS FILE IS A CRUCIAL MODULE THAT THE BIBLEAPP 
COULD NOT LIVE WITHOUT.
It contains many functions for cleaning up strings, lists
and other such things.
'''
def trim(string):
  '''Replaces all occurances of space with emptey space.'''
  new_string = string.replace(" ", "")
#//   
def join(arr):
  #old version
  string = str(arr)
  arr_syms = ["[", ",", "]", " ", "'"]
  for sym in arr_syms:
    string = string.replace(sym, " ")
  return string
#//
def join_space(arr):
   string = str(arr)
   arr_syms = ["[", ",", "]", " ", "'"]
   for sym in arr_syms:
     string = string.replace(sym, " ")
   return string
#//
def verse_str(arr):
  string = str(arr)
  arr_syms = ["\n", "' '", "[", "]"]
  for sym in arr_syms:
    string = string.replace(sym, "")
  return string
#//   
def join_underscore(arr):
   string = str(arr) 
   arr_syms = ["[", ",", "]", "'"]
   for sym in arr_syms:
     string = string.replace(sym, " ")
   string = string.replace(" ", "_")
   return string
#//
def replace(str):
  result = str.replace("_", " ")
  return result 
#//   
def search(list, item):
    for i in range(len(list)):
        if list[i] == item:
            return list[i]
    return False
#// 
def remove_underscore(s):
  return s.replace("_", " ")
#//
def clean(str):
  '''This function takes a string and replaces underscores with a space and the file extension .txt with an empty string. It then returns the modified string with all lower case.'''
  str = str.replace("_", " ")
  return str.replace(".txt", "").lower()
#//
def disclean(str):
  '''This function takes a string and replaces spaces with underscores, puts everything in lower case, and adds the .txt extension.'''
  str = str.replace(" ", "_").lower()
  return f"{str}.txt"
#//
def x_first_space(str):
  chars = []
  for char in str:
    chars.append(char)
  if chars[0] == " ":
    chars[0] = ""
#add reverse order function to module for reversing the order of items in a list