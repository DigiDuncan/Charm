import simfile
from simfile.notes import NoteData
from simfile.sm import SMChart

with open("./charm/data/tests/discord/discord.sm") as f:
    simfile = simfile.load(f)

chart: SMChart = simfile.charts[-1]

notes = NoteData(chart)

chart
