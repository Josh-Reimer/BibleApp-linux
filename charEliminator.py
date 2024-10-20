'''
DO NOT DELETE!
charEliminator.py is a crucial module and is referenced by several
other scripts so its obvious that its not to be deleted.
'''
def onlyVerses(file):
  '''onlyVerse returns an array of only verses in the book specified'''
  book = open(file).readlines()
  allNums = []
  for line in book:
    for char in line:
      if char.isdigit():
        allNums.append(line)
  return allNums 
def remove_only_chars(arr):
  '''remove_only_chars takes an list of verses and returns an list with only items that contain numbers'''
  result = []
  for item in arr:
    for char in item:
      if char.isdigit():
        result.append(item)
  return result