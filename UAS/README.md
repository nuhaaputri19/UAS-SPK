# UAS spk_web

## Install requirements

    pip install -r requirements.txt

## Run the app
to run the web app simply  use

    python main.py

## Usage
Install postman 
https://www.postman.com/downloads/

get restoran list
<img src='img/Screenshot postman 1.png' alt='restoran list'/>

get recommendations saw
<img src='img/Screenshot postman 2.png' alt='recommendations saw'/>

get recommendations wp
<img src='img/Screenshot postman 3.png' alt='recommendations wp'/>

### TUGAS UAS
Implementasikan model yang sudah anda buat ke dalam web api dengan http method `POST`

INPUT:
{
    "harga": 2, 
    "kualitas_pelayanan": 3, 
    "rating_makanan": 4, 
    "suasana": 2, 
    "lokasi": 5
}

OUTPUT (diurutkan / sort dari yang terbesar ke yang terkecil):

post recommendations saw
<img src='img/Screenshot postman 4.png' alt='recommendations saw'/>

post recommendations wp
<img src='img/Screenshot postman 5.png' alt='recommendations wp'/>
