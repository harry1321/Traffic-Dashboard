# Traffic-Dashboard
### About 
This is an unofficial traffic data dashboard mainly using python dash package for implemention. All data were collected from [Freeway Bureau, MOTC](https://tisvcloud.freeway.gov.tw/). This dashboard focuses on the north-bound of No. 5 freeway, and can generates four types of graphs which are fundamental diagram, speed-flow diagram, traffic flow time series graph and heatmap showing speed over time and locations.

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
![demonstration](https://i.imgur.com/QVfNU6g.gif)
