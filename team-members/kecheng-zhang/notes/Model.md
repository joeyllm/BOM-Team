# Specification

This document takes notes of the important information of the models.

## NowCastNet

Developed by Tsinghua University, see ["Skilful nowcasting of extreme precipitation with NowcastNet"](https://www.nature.com/articles/s41586-023-06184-4).

### Model Architecture

The architecture contains:
 - **Evolution Network**: Evolution Network uses Physics-Informed Neural Network (PINN) to determine the physics in a medium scale (20km). 
 - **Generation Network**: Generation Network learn the small dynamics in a fine scale (1km) under the physics constraints of the Evolution Network.

### Data

The features of data:
 - **Spatial Resolution**: 1km
 - **Temporal Resolution**: 10 min
 - **Input**: 9 steps (90min)
 - **Output**: 20 steps (200min) but takes only first 18 steps (3h)

## Liquid Neural Network

This model architecture is said to be super efficient with time-series related tasks.

> Only 19 neurons are needed for self-driving cars.

- Powerful and efficient
- Can learn while performing tasks
- New and hard to train

Deeper research of this LNN is needed to evaluate the feasibility for this project.