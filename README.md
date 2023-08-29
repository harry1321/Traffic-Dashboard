# Traffic-Dashboard
### About 
This is an unofficial traffic dashboard used python dash package for implemention and data were collected from the Freeway Bureau of the Ministry of Transportation and Communications ([MOTC](https://tisvcloud.freeway.gov.tw/)). The dashboard focuses on the northbound lanes of the No. 5 freeway and can generate four types of graphs: a fundamental diagram, a speed-flow diagram, a traffic flow time series graph, and a heatmap that shows speed over time and location.

### File Description
The app.py file depolys a local server and which can demonstrates the dashboard.(Running on http://127.0.0.1:8050/)

The layouts.py file defines the page layout which is seperate into three parts：description section, data filters section and graph area.

The callbacks.py file does two things：load-in the dataset and update graphs based on the filiters.

The vddata.py file contain functions used to load data and preprocess them.

The vdplot.py file contain graphing functions.

### Demonstration
Run this dashboard on local：
```
$ python __init__.py
```
![demonstration](/assets/Dash_-_Google_Chrome_2023-02-01_21-08-55_AdobeExpress.gif)  

This dashboard is currently live on：https://traffic-dashboard.onrender.com  
If you have any thoughts or suggestions, please feel free to contact me via [email](r08521524@ntu.edu.tw).
