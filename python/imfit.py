# Code for reading in and analyzing output of imfit

import imfit_funcs as imfuncs


# dictionary mapping imfit function short names (as found in the config/parameter file) to
# corresponding 1-D Python functions in imfit_funcs.py, along with some useful information:
# "function" = corresponding imfit_funcs.py function, "nSkip" = the number of 2D-related 
# parameters to skip (e.g., PA, ellipticity), "ell" = index for ellipticity parameter, 
# if it exists, "a" = index or indices for semi-major-axis parameters (r_e, h, sigma, etc.)
imfitFunctionMap = {"Exponential": {"function": imfuncs.Exponential, "nSkip": 2, "ell": 1, "a": [3]}, 
				"Exponential_GenEllipse": {"function": imfuncs.Exponential, "nSkip": 3, "ell": 1, "a": [4]},
				"Sersic":  {"function": imfuncs.Sersic, "nSkip": 2, "ell": 1, "a": [4]},
				"Sersic_GenEllipse":  {"function": imfuncs.Sersic, "nSkip": 3, "ell": 1, "a": [5]}, 
				"Gaussian":  {"function": imfuncs.Gauss, "nSkip": 2, "ell": 1, "a": [3]},
				"Moffat": {"function": imfuncs.Moffat, "nSkip": 2, "ell": 1, "a": [3]},
				"BrokenExponential":  {"function": imfuncs.BrokenExp, "nSkip": 2, "ell": 1, "a": [3,4,5]}}



def ChopComments( theLine ):
	return theLine.split("#")[0]


def GetFunctionImageNames( baseName, funcNameList ):
	"""Generate a list of FITS filenames as would be created by makeimage in "--output-functions"
	mode.
	"""
	
	nImages = len(funcNameList)
	imageNameList = [ "%s%d_%s.fits" % (baseName, i + 1, funcNameList[i]) for i in range(nImages) ]
	return imageNameList


def ReadImfitConfigFile( fileName, minorAxis=False, pix=1.0, getNames=False, X0=0.0 ):
	"""Function to read and parse an imfit-generated parameter file
	(or input config file) and return a tuple consisting of:
	(list of 1-D imfit_funcs functions, list of lists of parameters).
	
	pix = scale in arcsec/pixel, if desired for plotting vs radii in arcsec.
	
	We assume that all functions have a center at x = 0; this can be changed by setting
	X0.
	
	Returns tuple of (functionList, trimmedParameterList)
	If getNames == True:
		Returns tuple of (functionNameList, functionList, trimmedParameterList)
	"""
	
	dlines = [ line for line in open(fileName) if len(line.strip()) > 0 and line[0] != "#" ]

	funcNameList = []
	paramMetaList = []
	currentParamList = []
	nLines = len(dlines)
	for line in dlines:
		trimmedLine = ChopComments(line)
		#print(trimmedLine)
		if trimmedLine.find("X0") == 0:
			continue
		if trimmedLine.find("Y0") == 0:
			continue
		if trimmedLine.find("FUNCTION") == 0:
			# if this isn't the first function, store the previous set of parameters
			if len(currentParamList) > 0:
				paramMetaList.append(currentParamList)
			# make a new parameter list for the new function
			currentParamList = [X0]
			pp = trimmedLine.split()
			fname = pp[1].strip()
			funcNameList.append(fname)
			continue
		else:
			pp = trimmedLine.split()
			newValue = float(pp[1])
			currentParamList.append(newValue)

	# ensure that final set of parameters get stored:
	paramMetaList.append(currentParamList)
	
	# process function list to remove unneeded parameters (and convert size measures
	# from major-axis to minor-axis, if requested)
	funcList = [ imfitFunctionMap[fname]["function"] for fname in funcNameList ]
	trimmedParamList = []
	nFuncs = len(funcList)
	for i in range(nFuncs):
		fname = funcNameList[i]
		nSkipParams = imfitFunctionMap[fname]["nSkip"]
		fullParams = paramMetaList[i]
		# calculate scaling factor for minor-axis values, if needed
		if minorAxis is True:
			print fname
			ellIndex = imfitFunctionMap[fname]["ell"]
			print ellIndex
			ell = fullParams[ellIndex+1]
			q = 1.0 - ell
		else:
			q = 1.0
		print i, fname
		smaIndices = imfitFunctionMap[fname]["a"]
		# convert length values to arcsec and/or minor-axis, if needed,
		for smaIndex in smaIndices:
			# +1 to account for X0 value at beginning of parameter list
			fullParams[smaIndex+1] = pix*q*fullParams[smaIndex+1]
		# construct the final 1-D parameter set for this function: X0 value, followed
		# by post-2D-shape parameters
		trimmedParams = [fullParams[0]]
		trimmedParams.extend(fullParams[nSkipParams+1:])
		trimmedParamList.append(trimmedParams)
		
	
	if getNames is True:
		return (funcNameList, funcList, trimmedParamList)
	else:
		return (funcList, trimmedParamList)


