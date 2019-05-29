
import argparse
import os
from subprocess import call
import glob
import paths

if __name__ == "__main__":

	# parse args
	parser = argparse.ArgumentParser(description='')

	parser.add_argument('subj_path')
	parser.add_argument('--rerun', action='store_true')

	args = parser.parse_args()

	subj_path = args.subj_path
	rerun = args.rerun

	subj_path_files = os.listdir(subj_path)

	raw_dirs = glob.glob(subj_path + "/*/raw")
	num_raw_dirs = len(raw_dirs)

	incomplete_sess = []

	for dir in raw_dirs:

		sess_path = "/".join(dir.split("/")[:-1])
		psd_path = sess_path + "/psd"

		ignore_glob = glob.glob(psd_path + "/_ignore_me.txt")
		psd_glob = glob.glob(psd_path + "/*.mat") + glob.glob(psd_path + "/*.png")

		if len(psd_glob) < 2 and ignore_glob == []:
			incomplete_sess.append(sess_path)

	num_incomplete = len(incomplete_sess)

	print("sessions found with raw data: " + str(num_raw_dirs))
	print("number of incomplete sessions: " + str(num_incomplete))

	for sess in incomplete_sess:
		print("\t" + sess)

	if rerun:

		# create file to rerun psd
		swarms_path = subj_path + "/_swarms"
		rerun_sesslist_fname = swarms_path + "/rerun_sesslist.txt"

		rerun_sesslist = open(rerun_sesslist_fname, 'w')

		for sess in incomplete_sess:
			rerun_sesslist.write(sess.split("/")[-1] + "\n")

		rerun_sesslist.close()

		print("recreating bash scripts for " + str(len(incomplete_sess)) + " sessions ")
		call(["python3", paths.psd_pipeline_dir + "/construct_bash_scripts.py", subj_path, "--sesslist", rerun_sesslist_fname, "--output_suffix", "rerun"])
