/* FILE: func_broken-exp.cpp ------------------------------------------- */
/*
 *   Function object class for a broken-exponential function, with constant
 * ellipticity and position angle (pure elliptical, not generalized).
 *   
 *   BASIC IDEA:
 *      Setup() is called as the first part of invoking the function;
 *      it pre-computes various things that don't depend on x and y.
 *      GetValue() then completes the calculation, using the actual value
 *      of x and y, and returns the result.
 *      So for an image, we expect the user to call Setup() once at
 *      the start, then loop through the pixels of the image, calling
 *      GetValue() to compute the function results for each pixel coordinate
 *      (x,y).
 *
 *   NOTE: Currently, we assume input PA is in *degrees* [and then we
 * convert it to radians] relative to +x axis.
 *
 *   MODIFICATION HISTORY:
 *     [v0.1]  31 Mar 2010: Created as modification of func_exp.cpp.
 */

// Copyright 2010--2022 by Peter Erwin.
// 
// This file is part of Imfit.
// 
// Imfit is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free
// Software Foundation, either version 3 of the License, or (at your
// option) any later version.
// 
// Imfit is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
// for more details.
// 
// You should have received a copy of the GNU General Public License along
// with Imfit.  If not, see <http://www.gnu.org/licenses/>.


/* ------------------------ Include Files (Header Files )--------------- */
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <string>

#include "func_broken-exp.h"

using namespace std;


/* ---------------- Definitions ---------------------------------------- */
const int   N_PARAMS = 7;
const char  PARAM_LABELS[][20] = {"PA", "ell", "I_0", "h1", "h2", "r_break", "alpha"};
const char  PARAM_UNITS[][30] = {"deg (CCW from +y axis)", "", "counts/pixel", "pixels",
								"pixels", "pixels", "1/pixels"};
const char  FUNCTION_NAME[] = "Broken-Exponential function";
const double  DEG2RAD = 0.017453292519943295;
const int  SUBSAMPLE_R = 10;

const char BrokenExponential::className[] = "BrokenExponential";


/* ---------------- CONSTRUCTOR ---------------------------------------- */

BrokenExponential::BrokenExponential( )
{
  
  nParams = N_PARAMS;
  functionName = FUNCTION_NAME;
  shortFunctionName = className;

  // Set up vectors of parameter labels and units
  for (int i = 0; i < nParams; i++) {
    parameterLabels.push_back(PARAM_LABELS[i]);
    parameterUnits.push_back(PARAM_UNITS[i]);
  }
  parameterUnitsExist = true;
  
  doSubsampling = true;
}


/* ---------------- PUBLIC METHOD: AdjustParametersForImage ------------ */
/// Rescale/adjust input function parameters using current set of image-description 
/// parameters
void BrokenExponential::AdjustParametersForImage( const double inputFunctionParams[], 
										double adjustedFunctionParams[], int offsetIndex )
{
  // PA, ell, I_0, h1, h2, r_b, alpha
  adjustedFunctionParams[0 + offsetIndex] = inputFunctionParams[0 + offsetIndex] - imageRotation;
  adjustedFunctionParams[1 + offsetIndex] = inputFunctionParams[1 + offsetIndex];
  adjustedFunctionParams[2 + offsetIndex] = intensityScale * inputFunctionParams[2 + offsetIndex];
  adjustedFunctionParams[3 + offsetIndex] = pixelScaling * inputFunctionParams[3 + offsetIndex];
  adjustedFunctionParams[4 + offsetIndex] = pixelScaling * inputFunctionParams[4 + offsetIndex];
  adjustedFunctionParams[5 + offsetIndex] = pixelScaling * inputFunctionParams[5 + offsetIndex];
  adjustedFunctionParams[6 + offsetIndex] = (1.0/pixelScaling) * inputFunctionParams[6 + offsetIndex];
}


/* ---------------- PUBLIC METHOD: Setup ------------------------------- */

void BrokenExponential::Setup( double params[], int offsetIndex, double xc, double yc )
{
  x0 = xc;
  y0 = yc;
  PA = params[0 + offsetIndex] - imageRotation;
  ell = params[1 + offsetIndex];
  I_0 = params[2 + offsetIndex ] * intensityScale;
  h1 = params[3 + offsetIndex ] * pixelScaling;
  h2 = params[4 + offsetIndex ] * pixelScaling;
  r_b = params[5 + offsetIndex ] * pixelScaling;
  alpha = params[6 + offsetIndex ] / pixelScaling;

  // pre-compute useful things for this round of invoking the function
  q = 1.0 - ell;
  // convert PA to +x-axis reference
  PA_rad = (PA + 90.0) * DEG2RAD;
  cosPA = cos(PA_rad);
  sinPA = sin(PA_rad);

  exponent = (1.0/alpha) * (1.0/h1 - 1.0/h2);
  // Calculate S [note that this can cause floating *underflow*, but that's OK]:
  double  S = pow( (1.0 + exp(-alpha*r_b)), (-exponent) );
  I_0_times_S = I_0 * S;
  delta_Rb_scaled = r_b/h2 - r_b/h1;
}


/* ---------------- PRIVATE METHOD: CalculateIntensity ----------------- */
// This function calculates the intensity for a broken-exponential function at radius r,
// with the various parameters and derived values (I_0*S, exponent, etc.)
// pre-calculated by Setup().
// NOTE: We assume that r >= 0, since GetValue() ensures that.

double BrokenExponential::CalculateIntensity( double r )
{
  double  I;
  
  // check for possible overflow in exponentiation if r >> r_b, and re-route around it:
  if ( alpha*(r - r_b) > 100.0 ) {
    // Outer-exponential approximation:
    I = I_0_times_S * exp(delta_Rb_scaled - r/h2);
  } else {
    // no danger of overflow in exponentiation, so use fully correct calculation:
    I = I_0_times_S * exp(-r/h1) * pow( 1.0 + exp(alpha*(r - r_b)), exponent );
  }
  return I;
}


/* ---------------- PUBLIC METHOD: GetValue ---------------------------- */

double BrokenExponential::GetValue( double x, double y )
{
  double  x_diff = x - x0;
  double  y_diff = y - y0;
  double  xp, yp_scaled, r, totalIntensity;
  int  nSubsamples;
  
  // Calculate x,y in component reference frame, and scale y by 1/axis_ratio
  xp = x_diff*cosPA + y_diff*sinPA;
  yp_scaled = (-x_diff*sinPA + y_diff*cosPA)/q;
  r = sqrt(xp*xp + yp_scaled*yp_scaled);
  
  nSubsamples = CalculateSubsamples(r);
  if (nSubsamples > 1) {
    // Do subsampling
    // start in center of leftmost/bottommost sub-pixel
    double deltaSubpix = 1.0 / nSubsamples;
    double x_sub_start = x - 0.5 + 0.5*deltaSubpix;
    double y_sub_start = y - 0.5 + 0.5*deltaSubpix;
    double theSum = 0.0;
    for (int ii = 0; ii < nSubsamples; ii++) {
      double x_ii = x_sub_start + ii*deltaSubpix;
      for (int jj = 0; jj < nSubsamples; jj++) {
        double y_ii = y_sub_start + jj*deltaSubpix;
        x_diff = x_ii - x0;
        y_diff = y_ii - y0;
        xp = x_diff*cosPA + y_diff*sinPA;
        yp_scaled = (-x_diff*sinPA + y_diff*cosPA)/q;
        r = sqrt(xp*xp + yp_scaled*yp_scaled);
        theSum += CalculateIntensity(r);
      }
    }
    totalIntensity = theSum / (nSubsamples*nSubsamples);
  }
  else
    totalIntensity = CalculateIntensity(r);

  return totalIntensity;
}


/* ---------------- PROTECTED METHOD: CalculateSubsamples ------------------------- */
// Function which determines the number of pixel subdivisions for sub-pixel integration,
// given that the current pixel is a distance of r away from the center of the
// broken-exponential function.
// This function returns the number of x and y subdivisions; the total number of subpixels
// will then be the return value *squared*.
int BrokenExponential::CalculateSubsamples( double r )
{
  int  nSamples = 1;
  
  // do subsampling of inner exponential only (same as for standard exponential)
  if ((doSubsampling) && (r < 10.0)) {
    if ((h1 <= 1.0) && (r <= 1.0))
      nSamples = min(100, (int)(2 * SUBSAMPLE_R / h1));
    else {
      if (r <= 3.0)
        nSamples = 2 * SUBSAMPLE_R;
      else
        nSamples = min(100, (int)(2 * SUBSAMPLE_R / r));
    }
  }
  return nSamples;
}


/* END OF FILE: func_broken-exp.cpp ------------------------------------ */
