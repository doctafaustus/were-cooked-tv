"""Save the video's Resolve project and export a dated .drp backup to local.js backupDir.

    py -3.10 resolve/backup.py crispy-cranberry-chicken
"""
import sys

from resolve_common import backup, connect, load


def main():
    cfg = load(sys.argv[1] if len(sys.argv) > 1 else "crispy-cranberry-chicken")
    r, pm, p = connect(cfg)
    backup(cfg, pm, p)


if __name__ == "__main__":
    main()
