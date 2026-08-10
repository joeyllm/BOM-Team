# Paper - SWIFT

This file addresses the potential issues in the SWIFT.

## Potential Issues

### Linear Interpolation of Wind Too Smooth

Simply using linear interpolation to interpolate the wind field might be too smooth.

A possible solution is to add AR(1) noise to the interpolated wind field to simulate turbulence.