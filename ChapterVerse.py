'''
DO NOT DELETE!
ChapterVerse.py is responsible for an entire feature
of the BibleApp! - the book-chapter-verse navigation feature.
It is referenced by some other scripts.
'''
import list_and_str_ops as list
def get_chap(file, chap):
  '''Use this function to get a chapter of the Bible as a list\nwith each verse as one list item.\n\nThis function takes two parameters.\nOne is the file name of the book\nof the Bible you want.\nThe other is the chapter number.'''
  opened_file = open(file,"r")
  verses = opened_file.readlines()
  chapters = [verse for verse in verses if verse.split(":")[0] == f"{chap}"]
  opened_file.close()
  return chapters

def get_verse(book,chap,ver):
  '''Use this function to get a single \nverse of the Bible.\n\nIt takes three parameters.\nFirst, the book of the Bible.\nThe second is the chapter number.\nThe third is the verse number.'''
  chapter = get_chap(book,chap)
  return chapter[ver - 1]
