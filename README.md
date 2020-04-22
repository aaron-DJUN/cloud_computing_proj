# CS5224 Project
## Group 18
## Personal Shopping Recommender (PSR)

Dataset: Original Amazon Product [Data](http://jmcauley.ucsd.edu/data/amazon/links.html) 

Note that we do not include model artifacts in our main submission due to the limitation of uploaded data size in Luminus. 

The models are named as `Knn_model.sav`, `SVDpp_model.sav` and `model_47000img_identification.h5`. We would upload them in a separate zipped file. 

### To Use (local test)
Run under `./PSR_SaaS`

Put `model_47000img_identification.h5` under `./psrPlatform/img_model` and `Knn_model.sav`, `SVDpp_model.sav` under `./psrPlatform/recom_model`

Some username with password can be found in `./testCases.txt`

e.g., username: `Thomas` password: `123456`

Sample pictures for testing image recognition can be found in `./psrPlatform/static/profile_pics/pics_for_testing_img_recog`

```
# python 3.7.0
pip install -r requirements.txt
sudo python run.py
```
