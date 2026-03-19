import { animate, utils, createTimeline, createAnimatable, createDraggable } from 'https://esm.sh/animejs';

animate('.square', {
    width: '200px',
    height: '200px',
    backgroundColor: 'red',
    easing: 'inOutQuad',
});