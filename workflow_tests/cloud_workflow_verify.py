import argparse
from wget import download
import os
import shutil
import filecmp
import sys
from time import sleep

from bioblend.galaxy import GalaxyInstance

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--api_key", type=str, help="Galaxy API token")
parser.add_argument("-g", "--galaxy_url", type=str, help="URL for galaxy instance. On cloudman instance, must use extension as well as domain")
parser.add_argument("-c", "--comparefile", type=str, help="Data link 1")
args = parser.parse_args()

api_key = args.api_key
galaxy_url = args.galaxy_url
comparefile = args.comparefile

#Connect to Galaxy
gi = GalaxyInstance(url=galaxy_url, key=api_key, verify = False)

#prep to download most recent dataset in history
history_id = gi.histories.get_current_history()["id"]
wf = dict(gi.workflows.get_workflows()[0])["id"]
wf = gi.workflows.export_workflow_dict(wf)
files = []
for step in range (0,len(wf["steps"])):
    if wf["steps"][str(step)]["type"] == "data_input":
        files.append([step, "data_input"])
    for i in wf["steps"][str(step)]["outputs"]:
        files.append([step, i["name"], i["type"]])
files = len(files)


attempt_count =  0
while attempt_count <= 10:
    if len(gi.histories.get_current_history()['state_ids']['ok']) == files and len(gi.histories.get_current_history()['state_ids']['queued']) == 0:
        data = gi.histories.get_current_history()['state_ids']['ok'][-1]
        #print(data)
        dataset = gi.datasets.show_dataset(history_id, data)
        gi.datasets.download_dataset(data, file_path = "./outfile.txt", use_default_filename = False)
        try:
            filecmp.cmp("test.txt", "outfile.txt", shallow = False) == True
        except:
            exit("WF test failed: files do not match")
        print("HELP")
        sys.exit(0)
    else:
        if attempt_count < 10:
            sleep(6)
            attempt_count += 1
        else:
            print("NOPE")
            raise Exception("Took more than a minute to find dataset. WF likely didn't complete.")
