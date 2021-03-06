#!/usr/bin/env python

# script for generating distribution tarballs

import sys, os, shutil, optparse, tarfile, subprocess, copy
import markdown

sys.path.append(os.getcwd())
import distribution_manifest as dm

# where to copy binary (or source) tarballs when completed (specialized for
# Linux virtual machines on MacBook Pro and local web-site directory for Mac
# versions)
LINUX_DEST = "/media/sf_vbox_shared/"
MAC_DEST = "/Users/erwin/Documents/Working/web_site_new/resources/imfit/"
MAC_DEST_BIN = "/Users/erwin/Documents/Working/web_site_new/resources/imfit/binaries/"

MAC_CHANGELOG_MD = "CHANGELOG.md"
MAC_CHANGELOG_DEST = "/Users/erwin/Documents/Working/web_site_new/resources/imfit/CHANGELOG.html"

VERSION_STRING = "1.3.1"

os_type = os.uname()[0]   # "Darwin", "Linux", etc.
os_machine_type = os.uname()[4]   # "x86-64", etc.

# basic scons command (specifies use of OpenMP and static linking)
scons_string = "scons --static"

SOURCE_TARFILE = "imfit-%s-source.tar.gz" % VERSION_STRING
if (os_type == "Darwin"):   # OK, we're compiling on Mac OS X
	BINARY_TARFILE = "imfit-%s-macintel.tar.gz" % VERSION_STRING
	BINARY_TARFILE_OLDMAC = "imfit-%s-macintel_10.6-10.7.tar.gz" % VERSION_STRING
	# ensure that we use GCC-5.1 for all compilation
	scons_string += " --use-gcc"
	scons_string_oldmac = scons_string + " --old-mac"
	SOURCE_COPY_DEST_DIR = MAC_DEST
	BINARY_COPY_DEST_DIR = MAC_DEST_BIN
else:
	# assume it's Linux
	if os_machine_type == "x86_64":
		BINARY_TARFILE = "imfit-%s-linux-64.tar.gz" % VERSION_STRING
	else:
		BINARY_TARFILE = "imfit-%s-linux-32.tar.gz" % VERSION_STRING
	BINARY_COPY_DEST_DIR = LINUX_DEST
	SOURCE_COPY_DEST_DIR = LINUX_DEST


# Create dictionaries holding subdirectory names and lists of associated files
documentationFileDict = {"dir": "docs", "file_list": dm.documentation_files.split()}
coreFileDict = {"dir": "core", "file_list": dm.source_files_core.split()}
#cFileDict = {"dir": "c_code", "file_list": dm.source_files_c.split()}
solversFileDict = {"dir": "solvers", "file_list": dm.source_files_solvers.split()}
funcObjFileDict = {"dir": "function_objects", "file_list": dm.source_files_funcobj.split()}
exampleFileDict = {"dir": "examples", "file_list": dm.example_files.split()}
pythonFileDict = {"dir": "python", "file_list": dm.python_files.split()}
testFileDict = {"dir": "tests", "file_list": dm.test_files.split()}


# Lists of files:
binary_only_file_list = dm.binary_only_files.split()
misc_required_files_list = dm.misc_required_files.split()
testing_scripts_list = dm.testing_scripts.split()

# header_file_list = [fname + ".h" for fname in dm.source_header_files_top.split()]
# c_file_list = [fname + ".c" for fname in dm.source_files_c.split()]
# toplevel_source_list = c_file_list + header_file_list

documentation_file_list = [ documentationFileDict["dir"] + "/" + fname for fname in documentationFileDict["file_list"] ]

example_file_list = [ exampleFileDict["dir"] + "/" + fname for fname in exampleFileDict["file_list"] ]
python_file_list = [ pythonFileDict["dir"] + "/" + fname for fname in pythonFileDict["file_list"] ]
test_file_list = [ testFileDict["dir"] + "/" + fname for fname in testFileDict["file_list"] ]

solvers_file_list_cpp = [ solversFileDict["dir"] + "/" + fname + ".cpp" for fname in solversFileDict["file_list"] ]
solvers_file_list_h = [ solversFileDict["dir"] + "/" + fname + ".h" for fname in solversFileDict["file_list"] ]
solvers_file_list = solvers_file_list_h + solvers_file_list_cpp

core_file_list_cpp = [ coreFileDict["dir"] + "/" + fname + ".cpp" for fname in coreFileDict["file_list"] ]
core_file_list_h = [ coreFileDict["dir"] + "/" + fname + ".h" for fname in dm.source_header_files_core.split() ]
core_file_list = core_file_list_h + core_file_list_cpp

# c_file_list_cpp = [ cFileDict["dir"] + "/" + fname + ".c" for fname in cFileDict["file_list"] ]
# c_file_list_h = [ cFileDict["dir"] + "/" + fname + ".h" for fname in cFileDict["file_list"] ]
# c_file_list = c_file_list_h + c_file_list_cpp

funcobj_file_list_cpp = [ funcObjFileDict["dir"] + "/" + fname + ".cpp" for fname in funcObjFileDict["file_list"] ]
funcobj_file_list_h = [ funcObjFileDict["dir"] + "/" + fname + ".h" for fname in funcObjFileDict["file_list"] ]
#funcobj_file_list_h.append(funcObjFileDict["dir"] + "/" + "definitions.h")
funcobj_file_list = funcobj_file_list_h + funcobj_file_list_cpp


allFileLists = [binary_only_file_list, misc_required_files_list, documentation_file_list,
				example_file_list, python_file_list, testing_scripts_list, test_file_list, solvers_file_list,
				core_file_list, funcobj_file_list]
allFileLists_source = [misc_required_files_list, documentation_file_list,
				example_file_list, python_file_list, testing_scripts_list, test_file_list, solvers_file_list,
				core_file_list, funcobj_file_list]
subdirs_list = ["docs", "examples", "python", "tests", "function_objects", "solvers", "core"]



def TrimSConstruct( ):
	lines = open("SConstruct").readlines()
	nLines = len(lines)
	for i in range(nLines):
		if lines[i].startswith("# *** Other programs"):
			lastLineNumber = i
	outf = open("SConstruct_export", 'w')
	for line in lines[0:lastLineNumber]:
		outf.write(line)
	outf.close()


def MakeDistributionDir( mode="binary" ):
	distDir = "imfit-%s/" % VERSION_STRING
	# create distribution subdirectories, if needed
	if not os.path.exists(distDir):
		os.mkdir(distDir)
	for subdir in subdirs_list:
		if not os.path.exists(distDir + subdir):
			os.mkdir(distDir + subdir)
	# copy files to distribution subdirectory
	if (mode == "binary"):
		fileLists = allFileLists
	else:
		fileLists = allFileLists_source
	for fileList in fileLists:
		print fileList
		for fname in fileList:
			print("%s -> %s" % (fname, distDir + fname))
			shutil.copy(fname, distDir + fname)
	# copy misc. files requring renaming
	# copy trimmed version of SConstruct
	TrimSConstruct()
	shutil.copy("SConstruct_export", distDir + "SConstruct")


def MakeFatFile( file1, file2, outputName ):
	cmdText = "lipo -create {0} {1} -output {2}".format(file1, file2, outputName)
	subprocess.check_output(cmdText, shell=True)
	
def MakeFatBinaries( ):
	"""We need this because we now default to using GCC 5.1, which cannot make
	"fat" binaries by default.
	We only do this for the "oldmac" case (Mac OS X 10.6 and 10.7), since
	no one is trying to run 32-bit programs on 10.8 or later.
	"""

	print("   Calling SCons to generate 32-bit imfit binary for Mac OS 10.6/10.7...")
	subprocess.check_output(scons_string_oldmac + " --32bit" + " imfit", shell=True)
	shutil.move("imfit", "imfit32")
	print("   Calling SCons to generate 64-bit imfit binary for Mac OS 10.6/10.7...")
	subprocess.check_output(scons_string_oldmac + " imfit", shell=True)
	shutil.move("imfit", "imfit64")
	print("Merging into combined 32-bit/64-bit binary...")
	MakeFatFile("imfit32", "imfit64", "imfit")

	print("   Calling SCons to generate 32-bit makeimage binary for Mac OS 10.6/10.7...")
	subprocess.check_output(scons_string_oldmac + " --32bit" + " makeimage", shell=True)
	shutil.move("makeimage", "makeimage32")
	print("   Calling SCons to generate 64-bit makeimage binary for Mac OS 10.6/10.7...")
	subprocess.check_output(scons_string_oldmac + " makeimage", shell=True)
	shutil.move("makeimage", "makeimage64")
	print("Merging into combined 32-bit/64-bit binary...")
	MakeFatFile("makeimage32", "makeimage64", "makeimage")

def MakeOldMacBinaries( ):
	"""This is for making 64-bit binaries for Mac OS X 10.6 or 10.7.
	"""

	print("   Calling SCons to generate 64-bit imfit binary for Mac OS 10.6/10.7...")
	subprocess.check_output("scons -c", shell=True)
	subprocess.check_output(scons_string_oldmac + " imfit", shell=True)
	print("   Calling SCons to generate 64-bit makeimage binary for Mac OS 10.6/10.7...")
	subprocess.check_output(scons_string_oldmac + " makeimage", shell=True)
	

def MakeBinaries( mode=None ):
	# Generate appropriate binaries
	if (mode is None):
		# Mac OS 10.8 or newer, or Linux
		print("   Calling SCons to generate imfit binary...")
		subprocess.check_output(scons_string + " imfit", shell=True)
		print("   Calling SCons to generate makeimage binary...")
		subprocess.check_output(scons_string + " makeimage", shell=True)
	else:
		# Mac OS 10.6 or 10.7
		#MakeFatBinaries()
		MakeOldMacBinaries()
	

def MakeBinaryDist( mode=None ):
	distDir = "imfit-%s/" % VERSION_STRING
	final_file_list = binary_only_file_list + misc_required_files_list + documentation_file_list + example_file_list
	
	if (mode is None):
		# Mac OS 10.8 or newer, or Linux
		binaryTarfile = BINARY_TARFILE
	else:
		# Mac OS 10.6 or 10.7
		binaryTarfile = BINARY_TARFILE_OLDMAC
	print("Generating tar file %s..." % binaryTarfile)
	tar = tarfile.open(binaryTarfile, 'w|gz') 
	for fname in final_file_list:
		tar.add(distDir + fname)
	tar.close()

	print("Copying gzipped tar file %s to %s..." % (binaryTarfile, BINARY_COPY_DEST_DIR))
	shutil.copy(binaryTarfile, BINARY_COPY_DEST_DIR)


def MakeSourceDist( ):
	distDir = "imfit-%s/" % VERSION_STRING
	final_file_list = example_file_list + misc_required_files_list + documentation_file_list
#	final_file_list += header_file_list
#	final_file_list += c_file_list
#	final_file_list += cplusplus_file_list
	final_file_list += funcobj_file_list
	final_file_list += solvers_file_list
	final_file_list += core_file_list
#	final_file_list += c_file_list
	final_file_list += python_file_list
	final_file_list += testing_scripts_list
	final_file_list += test_file_list
	final_file_list.append("SConstruct")
	
	tar = tarfile.open(SOURCE_TARFILE, 'w|gz') 
	for fname in final_file_list:
		tar.add(distDir + fname)
	tar.close()
	
	print("Copying gzipped tar file %s to %s..." % (SOURCE_TARFILE, SOURCE_COPY_DEST_DIR))
	shutil.copy(SOURCE_TARFILE, SOURCE_COPY_DEST_DIR)
	print("Generating HTML version of CHANGELOG.md and copying to %s..." % (MAC_CHANGELOG_DEST))
	markdown.markdownFromFile(input=MAC_CHANGELOG_MD, output=MAC_CHANGELOG_DEST)



def main(argv):

	usageString = "%prog [options]\n"
	parser = optparse.OptionParser(usage=usageString, version="%prog ")

	parser.add_option("--source-only", action="store_false", dest="binaryDist", default=True,
					  help="generate *only* the source distribution tarball")
	parser.add_option("--binary-only", action="store_false", dest="sourceDist", default=True,
					  help="generate *only* the binary-only distribution tarball")

	(options, args) = parser.parse_args(argv)
	
	print("\nMaking distribution directory and copying files into it...")
	if options.binaryDist is True:
		if (os_type == "Darwin"):
			print("\nGenerating binary-only Mac distribution (%s)..." % BINARY_TARFILE)
			MakeBinaries()
			MakeDistributionDir(mode="binary")
			MakeBinaryDist()
			print("Generating binary-only Mac distribution for 10.6/10.7 (%s)..." % BINARY_TARFILE_OLDMAC)
			MakeBinaries(mode="oldmac")
			#MakeDistributionDir()
			MakeBinaryDist(mode="oldmac")
		else:
			print("\nGenerating binary-only Linux distribution (%s)..." % BINARY_TARFILE)
			MakeBinaries()
			MakeDistributionDir(mode="binary")
			MakeBinaryDist()
	if options.sourceDist is True:
		print("\nGenerating source distribution (%s)..." % SOURCE_TARFILE)
		MakeDistributionDir(mode="source")
		MakeSourceDist()
	
	print("Done!\n")



if __name__ == "__main__":
	main(sys.argv)

