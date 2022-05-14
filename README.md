# NBA game prediction
## General info
Our project is trying to predict the results of the NBA games.<br> 
We built a dynamic machine learning model and connected it to a dashboard showing the results of the prediction for the games in the coming week

## Project structure
* notebooks - Contains the research work we did to build the model and prepare the data
* train_model - Contains the code for geting new data, preprocessing and rebuilding the model (Should be scheduled for once a day)
* dash-app - Dashboard that loads the newly built model, and presents the prediction of the selected game
## Quick setup
1.Install prerequisite ``` pip install -r requirements.txt ```<br /> 
2.Get credentials from rapid-api:https://rapidapi.com/api-sports/api/api-nba and insert to .env file  <br /> 
3.Run train_model/main.py - for collecting data ,preprocessing and rebuilding model<br /> 
4.run dash-app/app.py and open dashboard from http://127.0.0.1:8050/<br /> 


## Dashboard 
![image](https://user-images.githubusercontent.com/70323589/168440995-d98be4f2-a4fb-4931-bc3e-cd0022acca03.png)

