# instagram-emotion-x

Flask server hosting a webapp for Instagram profile image emotion analysis.

```
Edit line 200 of /templates/form-iframe.html with your frontail url

frontail -p 9999 --ui-hide-topbar z.log 
python3 final-server.py > z.log
```
Spawns a web server on port 80 with the app.


Grabs all the profile images then does an emotional analysis using a self-hosted DeepFace API and frontail then plots it into a chart.
![alt text](https://www.tokyochronos.net/upload/nfzo49p7.gif)
Requires instaloader, flask, and deepface packages and frontail.


