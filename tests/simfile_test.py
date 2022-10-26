import simfile
from simfile.notes import NoteData

with open("./charm/data/tests/discord/discord.sm") as f:
    simfile = simfile.load(f)

chart = simfile.charts[-1]

notes = NoteData(chart)

for note in notes:
    print(note.column)