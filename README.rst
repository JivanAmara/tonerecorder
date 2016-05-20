A django application for the recording of pinyin syllables.

Dependencies:
 - hanzi-basics (For PinyinSyllable model)

normalize_samples.py provides analytical procedures to convert original recordings to standardized
.wav format data for further analysis.  This includes stripping silence and normalizing volume.

file_samples.py provides tools to import/export samples from database to files.

