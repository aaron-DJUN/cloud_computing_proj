#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# image recognition 
# Note: change path when necessary
import os
import pickle
import numpy as np
from keras.preprocessing import image
from keras.models import load_model

if __name__ == '__main__':
    # load artifacts
    label2idx = pickle.load(open('model/img_label2idx.pkl', 'rb')) # change path when necessary
    idx2label = {i:j for j, i in label2idx.items()}
    ## load the deep learning model
    model = load_model("model/model_47000img_identification.h5") 
    
    # unittest
    fnames = './model_test/imgs'
    img = image.load_img(os.path.join(fnames,'1886846774.jpg'), target_size=(150, 150))
    x = np.expand_dims(image.img_to_array(img), axis=0)/255.0
    pred = model.predict(x)
    
    # get top 3 product id with confidence
    pred = pred.flatten()
    top_3_idx = pred.argsort()[::-1][:3]
    top_3_items = {idx2label[i]:np.round(pred[i],10) for i in top_3_idx}
    print(top_3_items)
