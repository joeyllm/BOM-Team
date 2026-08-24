# Data

## Time Interpolation Methods for Wind U, V Components

### Method Comparison

| Method | Description | Pros / Cons | Best For |
|--------|-------------|-------------|----------|
| Scalar interpolation | Interpolate U, V independently (linear, spline) | Simple, fast / unrealistic when direction changes rapidly | High-res data, short intervals |
| Physical field interpolation | Interpolate divergence/vorticity, then reconstruct U, V | Physically consistent / complex | Requires accurate convergence/divergence |
| Complex EOF | Interpolate principal-mode time coefficients, reconstruct | Captures propagating systems / costly | Cyclones, fronts |
| FFT | Interpolate in frequency domain, inverse transform | Keeps periodicity / non-physical oscillations | Strong periodic signals |
| Optimal interpolation | Fuse multi-source data with optimal weights | High accuracy / needs error estimates | Multi-source, high precision |

### Key Precaution: Rotation on the Sphere

Never interpolate U, V directly across large lat/lon ranges — "east/north" directions differ by location. Rotate the vector by angle \( rot \):

$$
u_{new} = u\cos(rot) + v\sin(rot), \quad v_{new} = -u\sin(rot) + v\cos(rot)
$$

### Recommendations

- Default: **scalar interpolation** (simple, sufficient for most cases).
- Propagating systems: **Complex EOF**; periodic signals: **FFT**.
- Multi-source fusion: **optimal interpolation**.
- Always rotate vectors over large domains.
