
import argparse
import os
import paths
import shutil


def write_session_scripts(sess_path, fresh_write):

	psd_dir = sess_path + "/psd"

	if fresh_write is True and os.path.isdir(psd_dir):
		print("fresh write (deleting psd/ dir)")
		shutil.rmtree(psd_dir)

	psd_scripts_dir = psd_dir + "/scripts"

	if os.path.isdir(psd_dir) is False:
		os.mkdir(psd_dir)

	if os.path.isdir(psd_scripts_dir) is False:
		os.mkdir(psd_scripts_dir)

	psd_log_fpath = psd_scripts_dir + "/_psd.log"
	psd_bash_fpath = psd_scripts_dir + "/psd.sh"
	psd_bash = open(psd_bash_fpath, 'w')

	# write the sbatch header for sub_cmd bash file
	sbatch_header = []
	sbatch_header.append("#!/bin/bash")
	sbatch_header.append("#SBATCH --mem=10g")
	sbatch_header.append("#SBATCH --cpus-per-task=1")
	sbatch_header.append("#SBATCH --error=" + psd_log_fpath)
	sbatch_header.append("#SBATCH --output=" + psd_log_fpath)
	sbatch_header.append("#SBATCH --gres=lscratch:15")

	for l in sbatch_header:
		psd_bash.write(l + "\n")

	psd_bash.write("\n\n")

	psd_bash.write("echo \"SLURM_JOB_ID = $SLURM_JOB_ID\" &> " + psd_log_fpath + "\n")

	psd_bash.write("tar -C /lscratch/$SLURM_JOB_ID -xf /usr/local/matlab-compiler/v94.tar.gz;")

	matlab_command = "cd " + paths.extract_psd_var_dir + "/_extract_psd_var; ./run_extract_psd_var_swarm.sh " + paths.matlab_compiler_ver_str

	sub_cmd = []
	sub_cmd.append(matlab_command)
	sub_cmd.append("sess_path")
	sub_cmd.append(sess_path)

	sub_cmd.append("&> " + psd_log_fpath)

	psd_bash.write(" ".join(sub_cmd) + "\n")

	psd_bash.close()

	return(psd_bash_fpath)


if __name__ == "__main__":

	# parse args
	parser = argparse.ArgumentParser(description='')

	parser.add_argument('subj_path')
	parser.add_argument('--sesslist', default="")
	parser.add_argument('--output_suffix', default="initial")
	parser.add_argument('--fresh_write', action='store_true')

	args = parser.parse_args()

	subj_path = args.subj_path
	sesslist_fname = args.sesslist
	output_suffix = args.output_suffix
	fresh_write = args.fresh_write

	# get session list
	if sesslist_fname != "":

		sesslist = open(sesslist_fname)
		subj_path_files = [l.strip("\n") for l in sesslist]
		sesslist.close()

	else:

		subj_path_files = os.listdir(subj_path)

	subj_path_files.sort()

	print("sessions: " + str(len(subj_path_files)))

	swarm_path = subj_path + "/_swarms"

	if os.path.isdir(swarm_path) is False:
		os.mkdir(swarm_path)

	swarm_fpath = swarm_path + "/psd_%s_swarm.sh" % output_suffix
	big_bash_fpath = swarm_path + "/psd_%s_big_bash.sh" % output_suffix

	swarm = open(swarm_fpath, 'w')
	swarm.write("swarm -g 10 -b 10 -t 1 --time 2:00:00 --gres=lscratch:15 --merge-output --logdir " + swarm_path + "/log_dump -f " + big_bash_fpath)
	swarm.close()

	big_bash = open(big_bash_fpath, 'w')

	for sess in subj_path_files:

		print("")
		print("looking at session " + sess, end="")

		sess_path = subj_path + "/" + sess

		if os.path.isdir(sess_path) is True:

			print(" ... is a directory", end="")

			if os.path.isdir(sess_path + "/raw"):

				cmd = write_session_scripts(sess_path, fresh_write)
				big_bash.write("bash " + cmd + "\n")

	big_bash.close()
