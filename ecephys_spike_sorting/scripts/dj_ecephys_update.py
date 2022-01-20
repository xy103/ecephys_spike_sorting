from sglx_multi_run_pipeline_js import run_ecephys 
import sys 
import os

ks_dj_pipeline_path = r'C:\Users\joshs\Documents\GitHub\ks-dj-pipeline'
sys.path.append(ks_dj_pipeline_path)
# now import datajoint stuff
from dj_ephys_utils import reformat_np_dir,update_Date
from CY_schema_table import BehaSession
from JS_ephys_tables import EphysSession, SpikeSortingResults

# reformat sglx sessions within DJ-compatible nested directory structure
reformat_np_dir()
# add new dates to Date() manual table
update_Date()
# update BehaSession and EphysSession tables
BehaSession().populate()
EphysSession().populate()

results_directory = r'Z:\HarveyLab\Tier1\Cindy\ProcessedEphys'

# Look for ephys sessions that don't have spikesorting results
session_keys , ephys_paths = ((EphysSession() & "probe = 'NP1'") - SpikeSortingResults()).fetch("KEY","ephys_path")

print("Now beginning ecephys processing of ephys sessions that have not been spike-sorted yet")
for this_key,this_unprocessed_np_path in zip(session_keys,ephys_paths): 
    print("Processing session at: ",this_unprocessed_np_path)

    run_ecephys(this_unprocessed_np_path,results_directory)

    # file formatting from sglx_multi_run_pipeline_js.py
    npx_directory_full = os.path.join(this_unprocessed_np_path,os.listdir(this_unprocessed_np_path)[0])
    session_name_gx_tx = [x for x in os.listdir(npx_directory_full) if x[-4:] == ".bin" ][0].split('.')[0]
    session_name = session_name_gx_tx[:session_name_gx_tx.index('_g')]
    gate = session_name_gx_tx[session_name_gx_tx.index('_g')+2]
    these_recording_specs = [session_name, gate, 'start,end','0', ['thalamus'] ]
    npx_directory_split = this_unprocessed_np_path.split(os.sep)
    catGT_dest = os.path.join(results_directory,npx_directory_split[-4],npx_directory_split[-3],npx_directory_split[-2],npx_directory_split[-1])
    output_dest = os.path.join(catGT_dest,'catGT_' + these_recording_specs[0] + '_g' + these_recording_specs[1])

    # # Insert new file processed results path into SpikeSortingResults manual table
    new_processed_entry = {**this_key, **{"ecephys_spike_sorting_results_path" : output_dest,"run_specs" : these_recording_specs}}
    print(new_processed_entry)
    SpikeSortingResults().insert1(new_processed_entry)
    print("Inserted new entry in SpikeSortingResults: ",new_processed_entry) 