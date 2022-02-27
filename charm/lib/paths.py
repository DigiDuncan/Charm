from pathlib import Path

import appdirs


def getDataDir():
    appname = "SizeBot"
    appauthor = "DigiDuncan"
    datadir = Path(appdirs.user_data_dir(appname, appauthor))
    return datadir


# File paths
datadir = getDataDir()
winkpath = datadir / "winkcount.txt"
guilddbpath = datadir / "guilds"
telemetrypath = datadir / "telemetry"
thispath = datadir / "thistracker.json"
changespath = datadir / "changes.json"
naptimepath = datadir / "naptime.json"
confpath = datadir / "sizebot.conf"
whitelistpath = datadir / "whitelist.txt"
