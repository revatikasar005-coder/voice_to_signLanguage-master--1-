import ytdownload,test01,speech_to_isl
import sys
""""
ytdownload.downloader("call accross")
test01.generateclip("call accross")

s=speech_to_isl.isl(sys.argv[1])

s=speech_to_isl.isl("I am reading a story")
"""

input_text = " ".join(sys.argv[1:]).strip()
if not input_text:
    print("No input text provided")
    sys.exit(1)

s = speech_to_isl.isl(input_text)

s = s.strip()
if not s:
    print("ISL output is empty")
    sys.exit(1)

ytdownload.downloader(s)
test01.generateclip(s)
print("done!")
