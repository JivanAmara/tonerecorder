A django application for the recording of pinyin syllables.

Dependencies:
 - hanzi-basics (For PinyinSyllable model)
 - django-user-agents (To ensure smart phones are used on recording page)

Add: 'django_user_agents.middleware.UserAgentMiddleware' to middleware of containing project.


normalize_samples.py provides analytical procedures to convert original recordings to standardized
.wav format data for further analysis.  This includes stripping silence and normalizing volume.

file_samples.py provides tools to import/export samples from database to files.

