/** @file
    \brief Subclass of OptionsBase blass for makemultimages-specific program options.
 *
 */
#ifndef _OPTIONS_MAKEMULTIMAGES_H_
#define _OPTIONS_MAKEMULTIMAGES_H_

#include <string>
#include <vector>

#include "definitions.h"
#include "definitions_multimage.h"
#include "options_base.h"


//! Derived class for holding various options for makeimage (set by command-line flags & options)
class MakeMultimagesOptions : public OptionsBase
{

  public:
    // Constructor:
    MakeMultimagesOptions( )
    {
      noConfigFile = true;
      configFileName = "";

      noOutputImageName = true;
      outputImageName = DEFAULT_MAKEMULTIMAGE_OUTPUT_FILENAME;
      functionRootName = "";
      noRefImage = true;
      referenceImageName = "";
  
      subsamplingFlag = true;
  
      noImageDimensions = true;
      nColumnsSet = false;
      nRowsSet = false;
      nColumns = 0;
      nRows = 0;
  
      psfImagePresent = false;
      psfFileName = "";
      psfOversampledImagePresent = false;
      psfOversampledFileName = "";
      psfOversamplingScale = 0;
      oversampleRegionSet = false;
      nOversampleRegions = 0;
  
      magZeroPoint = NO_MAGNITUDES;

      printImages = false;
      saveImage = true;
      saveExpandedImage = false;
      saveAllFunctions = false;

      printFluxes = false;
      estimationImageSize = DEFAULT_ESTIMATION_IMAGE_SIZE;
      timingIterations = 0;

      maxThreadsSet = false;
      maxThreads = 0;

      // TESTING
      imageInfoFile_exists = false;
    };

    // Extra data members (in addition to those in options_base.h):
    bool  noOutputImageName;
    std::string  outputImageName;

    std::string  functionRootName;
    bool  noRefImage;
    std::string  referenceImageName;

    bool  noImageDimensions;
    bool  nColumnsSet;
    bool  nRowsSet;
    int  nColumns;
    int  nRows;

    double  magZeroPoint;

    bool  printImages;
    bool  saveImage;
    bool  saveExpandedImage;
    bool  saveAllFunctions;  // save individual-function images

    bool  printFluxes;
    int  estimationImageSize;
  
    int  timingIterations;
    
    // TESTING
    std::string  imageInfoFile;
    bool  imageInfoFile_exists;
};


#endif  // _OPTIONS_MAKEMULTIMAGES_H_
