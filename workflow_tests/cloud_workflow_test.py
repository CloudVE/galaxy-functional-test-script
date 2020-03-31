import argparse
from wget import download
import os
import shutil

from bioblend.galaxy import GalaxyInstance

try: shutil.rmtree('tempdata')
except: pass

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--api_key", type=str, help="Galaxy API token")
parser.add_argument("-g", "--galaxy_url", type=str, help="URL for galaxy instance. On cloudman instance, must use extension as well as domain")
parser.add_argument("-1", "--file1", type=str, help="Data link 1")
parser.add_argument("-2", "--file2", type=str, help="Data link 2")
args = parser.parse_args()

api_key = args.api_key
galaxy_url = args.galaxy_url
file1 = args.file1
file2 = args.file2

#Connect to Galaxy
gi = GalaxyInstance(url=galaxy_url, key=api_key)

#Download data and upload to Galaxy
## UN-HARD CODE LATER
os.mkdir("tempdata")
data1 = "tempdata/fastq1.fq.gz"
data2= "tempdata/fastq2.fq.gz"
download(url = file1, out=data1)
download(url = file2, out=data2)
history_id = gi.histories.get_current_history()["id"]
gi.tools.upload_file(data1, history_id)
gi.tools.upload_file(data2, history_id)
shutil.rmtree("tempdata")

#prep data input for workflow
data_inputs = {}
peek = gi.histories.show_matching_datasets(history_id)
for x in range(0, len(peek)):
    data_inputs[str(x)] = {"id": peek[x]["id"], "src": 'hda'}

#Download workflow
gi.workflows.import_workflow_from_local_path("./Downloads/Galaxy-Workflow-cloud_test_wf.ga") #Change based on how retrieving the workflow
wf_id = dict(gi.workflows.get_workflows(name="cloud test wf")[0])["id"]

# #Invoke WF
gi.workflows.invoke_workflow(workflow_id = wf_id, inputs = data_inputs, history_id = history_id)
