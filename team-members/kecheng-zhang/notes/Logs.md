# Daily Logs

This file records the daily progress. Although I might not write them every single day, it will still cover the major events.

## Week 1

Not much of the ML part of the project is done this week. I basically spent most of the time on the website. 

### 2026-03-21

The website is built based on GitHub Pages and Jekyll.

Libraries include Three.js, Two.js, and Anime.js have been tested in the past few days to make a good background animation. It has been a headache, so finally I used just basic WebGL with the help of AI.

The animation uses Perlin Noise + FBM to generate the effect of a wind field. The idea is to combine the activated neurons (blue dots) of the neural network with the wind field to create a dynamic effect that fits the theme of the project.

In addition, I've been doing research on the architecture of the whole application. I think Electron + React + Pytorch + FastAPI should be nice.

Added some content to the website. The website still needs some design.

> AHHHHHH! It is so hard to make a good-looking website! I really need help!

### 2026-03-22

Kimi k-2.5 turns out to be really helpful in designing the website when given proper prompts. Now the website is basically complete.

## Week 2

### 2026-03-23

*PyEarthTool* is based on **FourCastNet**, which is very powerful in predicting medium-long term weather.

When searching the relavent informations, I found **NowCastNet**. Seems it is perfect for the project, I will work on it.

*Very Useful* Link:[Skilful nowcasting of extreme precipitation with NowcastNet](https://www.nature.com/articles/s41586-023-06184-4)