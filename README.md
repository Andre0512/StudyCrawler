# StudyCrawler

#### **This web crawler watches different pages of my university net and sends notifications to a telegram channel.**  

## Current features:
* Sending documents which the professors uploaded to the _MyStudy_ web page
* Sending a notification if the state of an exam has changed on the exam server
* Sending schedule if a new version is online

_This crawler was created for the _RheinAhrCampus_ of the _Hochschule Koblenz_ and only tested there. 
Maybe parts work at other German universities with similar portals, but I don't know._


## Installation (Linux)

1. Download this script  
`git clone htps://github.com/Andre0512/StudyCrawler.git && cd MyStudyCrawler`
2. Create a virtual environment (optional)  
`python3 -m venv ./venv && source ./venv/bin/activate`
3. Install requirements  
`pip install -r requirements.txt`
4. Add your personal data to `secrets.py`  
`mv secrets.py.default secrets.py && vim secrets.py`  
This can be a bit tricky, contact me if you have any questions.
5. Create entry in `/etc/crontab` to execute this script e.g. every three minutes  
`echo "*/3 *   * * *   $USER   $PWD/venv/bin/python $PWD/crawler.py" | sudo tee --append /etc/crontab`


## License

This project is under MIT-License. Have fun :)

## Screenshot

![Screenshot](img/screenshot.png?raw=true "Telegram Channel")
