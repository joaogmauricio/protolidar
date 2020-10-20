#!/usr/bin/python

import regex
import sys
import os
import argparse
from argparse import RawTextHelpFormatter
from git import Repo
from termcolor import colored

# limited up to 6 dimension arrays
POLLUTION_REGEX = regex.compile("([^][\s]+)(\[(?:(?>[^][]+)|(?2))*\])(\[(?:(?>[^][]+)|(?3))*\])(\[(?:(?>[^][]+)|(?4))*\])?(\[(?:(?>[^][]+)|(?5))*\])?(\[(?:(?>[^][]+)|(?6))*\])?(\[(?:(?>[^][]+)|(?7))*\])?\s*=[^==](.*)")

def walk(some_dir, recursive=False):
	some_dir = some_dir.rstrip(os.path.sep)
	assert os.path.isdir(some_dir)
	num_sep = some_dir.count(os.path.sep)
	for root, dirs, files in os.walk(some_dir):
		yield root, dirs, files
		num_sep_this = root.count(os.path.sep)
		if (not recursive) and (num_sep <= num_sep_this):
			del dirs[:]

def print_error(msg, color='', *args, **kwargs):
	if color == '':
		sys.stderr.write(msg + '\r\n')
	else:
		sys.stderr.write(colored(msg + '\r\n', color, *args, **kwargs))
	sys.stderr.flush()

def parse_args():
	parser = argparse.ArgumentParser(description="Prototype Pollution Code Scanner", formatter_class=RawTextHelpFormatter)

	parser.add_argument("-s", "--non-recursive", action="store_false", help="simply examine the target directory, without recursivity")
	parser.add_argument("-p", "--pickiness", type=int, choices=[0,1,2], default=2, help="sets 'pickiness' level (how strict the scan patters are)")

	group = parser.add_mutually_exclusive_group(required=True)

	group.add_argument("-d", "--directory", help="target directory")
	group.add_argument("-u", "--url-git", help="target git repo")

	return parser.parse_args()

def scan(dir, recursive=False, pickiness=2):
	# traverse the current directory
	for root, directories, filenames in walk(dir, recursive):
		for filename in filenames:
			# searches for *.js or *.ts files (excluding *.min.js ones)
			if not filename.endswith('.min.js') and (filename.endswith('.js') or filename.endswith('.ts')):
				# parses each file ...
				with open(os.path.join(root,filename)) as fp:
					# ... line by line
					for i,line in enumerate(fp.readlines()):
						# skip lines starting with // or if line > 400 chars
						if regex.match("^\s*\/\/", line) or len(line) > 400:
							continue
						# tries to find a potential pollution candidates
						for match in regex.findall(POLLUTION_REGEX, line):
							# removes empty groups
							match = filter(None, match)
							# extracts injection candidate (n-1 array dimension)
							candidateProto = match[-3][1:-1]
							candidateParam = match[-2][1:-1]
							candidateValue = match[-1]
							# excludes non-variable candidates
							if (pickiness == 0 and (not regex.match("^\"[^\"]*\"$|^'[^']*'$|^\d*$", candidateProto))) or (pickiness == 1 and (not regex.match("^\"[^\"]*\"$|^'[^']*'$|^\d*$|^\w$", candidateProto) and not regex.match("^\"[^\"]*\"$|^'[^']*'$|^\d*$|^\w$", candidateParam) and not regex.match("^undefined(;)?$", candidateValue.lower())) or (pickiness == 2 and (not regex.match("^\"[^\"]*\"$|^'[^']*'$|^\d*$|^\w$", candidateProto) and not regex.match("^\"[^\"]*\"$|^'[^']*'$|^\d*$|^\w$", candidateParam) and not regex.match("^\"[^\"]*\"(;)?$|^'[^']*'(;)?$|^\d*(;)?$|^true(;)?$|^false(;)?$|^undefined(;)?$", candidateValue.lower())))):
								print os.path.join(root,filename) + ":" + str(i) + "\t\t\t" + str.strip(line)


def main():
	args = parse_args()
	if args.directory:
		scan(args.directory, args.non_recursive, args.pickiness)
	elif args.url_git:
		target_dir = "./repos/" + args.url_git.split('/')[-1].split('.')[0]
		try:
			Repo.clone_from(args.url_git, target_dir)
			scan(target_dir, args.non_recursive, args.pickiness)
		except Exception as e:
			if "already exists" in e.stderr:
				print_error('WARNING: "{0}" already exists but I will scan it anyway.'.format(target_dir), 'yellow')
				scan(target_dir, args.non_recursive, args.pickiness)
			else:
				print_error(e, "red")

if __name__ == "__main__":
	main()
