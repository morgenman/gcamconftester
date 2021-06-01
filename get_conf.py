from gcamconftester import adb_command
from gcamconftester import gcam_package
import sys

config = sys.argv[1] if len(sys.argv) > 1 else "perrot043top.xml"
adb_command('root')
adb_command(f'pull /data/data/{gcam_package}/shared_prefs/{gcam_package}_preferences.xml {config}')