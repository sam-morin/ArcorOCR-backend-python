<div align="center">
  <a href="https://arcorocr.com" target="_blank">
    <img src="/pdf_512.png" alt="Logo" width="200">
  </a>

  <h1 align="center"><a href="https://arcorocr.com" target="_blank">ArcorOCR.com</a> | Backend</h1>

  <p align="center">
    <h3>PDF OCR for the OCR-less</h3>
    <!-- <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br /> -->
    <a href="https://arcorocr.com">View Live</a>
    ·
    <a href="https://github.com/sam-morin/ArcorOCR-backend-python/issues">Report Bug</a>
    ·
    <a href="https://github.com/sam-morin/ArcorOCR-backend-python/issues">Request Feature</a>
    .
    <a href="https://github.com/sam-morin/ArcorOCR-backend?tab=readme-ov-file#running">Build/Develop</a>
    .
    <a href="https://github.com/sam-morin/ArcorOCR-frontend">Frontend Repo</a>
  </p>
</div>

<br/>

Here lives the backend for ArcorOCR. 


## It's Python,

## uses OCRmyPDF,

## and runs with Gunicorn.


There are two endpoints:
 - `/upload` (perform OCR generation of the supplied file in POST)
 - `/upload/remove` (perform OCR removal of the supplied file in POST)

 Enjoy.


# Running

### Production

1. Pull and CD
```shell
git pull https://github.com/sam-morin/ArcorOCR-backend-python.git && cd ArcorOCR-backend
```

2. Build image
```shell
docker build . -t arcorocr-backend
```

3. Run image
```shell
docker run -d --restart unless-stopped -p PUBLIC_PORT:5000 arcorocr-backend
```

### Development

1. Pull and CD
```shell
git pull https://github.com/sam-morin/ArcorOCR-backend-python.git && cd ArcorOCR-backend
```

2. Install requirements.txt
```shell
pip install requirements.txt
```

3. Run it with Flask
```shell
python server.py
```

or, better yet..

3. Run it with Gunicorn
```shell
gunicorn -w 4 -b 0.0.0.0:5000 server:app --timeout 300
```