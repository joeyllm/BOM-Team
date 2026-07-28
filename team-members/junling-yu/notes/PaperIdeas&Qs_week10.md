


Questions related to masking:
Currently the paper just says \(M_t \in \{0,1\}^{H \times W}\) is used as the mask method. 
For more details, consider whether it is a shared masking for all variables, or one masking per variable, or one masking method per data source, or combined validity mask.
The paper also said “the mask channel allows the encoder to learn that these cells carry no information”, does the model really have the ability to learn, or it’s just an assumption? Besides, how do you deal with masked values in CNN? Is masking only applied in the loss function, or is it incorporated into the convolution operation itself (e.g. masked convolution, partial convolution, gated convolution)? Is it a better choice to use spatial interpolation or data assimilation techniques prior to convolution, rather than relying entirely on masked inputs?

sequence Flattening
When flattening the feature map(output of CNN) into tokens, usually we need to add spatial position encoding and stack temporal dimension (to let transformer know which part of the picture the information in the vector sequence is about), but since here we only use transformer to deal with time info, maybe we only add temporal encoding.
-And then, If the transformer models only temporal evolution, is temporal positional encoding alone sufficient?

Attention is expensive, how to save cost when using attention?
ViT(also used in Pangu weather)-send patch into transformer instead of pixel
swin transformer-window attention, attention focus on part of the image rather than all range
earthformer-cuboid attention(cuboid on both time and space)
Above methods are using transformer to deal with space, but the idea of cutting into patches/cuboids may also be used in our model
Even if we have access to supercomputer, we still need to deal with memory analysis, reduce the number of tokens, etc.(suggestion: add a model complexity analysis part in the research)

Why is H*W*C tensor better than graph-based, point-cloud, or irregular-grid representations, except for being easier to add new data sources?

Are we going to add prediction data into our data source in the future? Is it really meaningful using prediction to predict, the paper mentions forecast, correction, analysis, emulator, need to be more specific. (In other words, The paper mentions integrating forecast products as input data. What is the intended role of these products? If forecast products are already predictions, what additional information is the model expected to learn beyond simply reproducing the input forecasts?)

Loss function is too simple, Using only MAE/MSE typically encourages overly smooth predictions, especially for high-frequency weather structures. Other structural or physics-aware objectives measures to consider: gradient loss, SSIM, CRPS, spectral loss, physics loss.

Why are you building a model that is not physics-informed?(in other words, Given that atmospheric evolution is strongly governed by physical laws, why does the proposed model not incorporate any physics-informed constraints? Is this an intentional design choice?)

What is your story? Are you building a forecast model or representation?