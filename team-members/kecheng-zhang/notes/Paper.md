# Paper - SWIFT

This file addresses the potential issues in the SWIFT.

## Potential Issues

### Linear Interpolation of Wind Too Smooth

Simply using linear interpolation to interpolate the wind field might be too smooth.

A possible solution is to add AR(1) noise to the interpolated wind field to simulate turbulence.

### Variable Choice

Good variables are:
- `uwnd10m`
- `vwnd10m`
- `sfc_pres`
- `temp_scrn`

Bad variables are:
- `wndgust10m`: It cannot be interpolated.
- `accum_rain`: Interpolating this variable has little or no physical meaning, and it is basically 0.
