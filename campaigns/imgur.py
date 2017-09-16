import requests,os
def createPhotoImgur(photoBase64):
    imgurClientID = os.environ.get('IMGUR_CLIENT_ID')

    r = requests.post('https://api.imgur.com/3/image',
    headers={
        'Authorization': 'Client-ID ' + imgurClientID,
    },
    data={
        'image': photoBase64,
    })
    return r.json()
def deletePhotoImgur(deletehash):
    imgurClientID = os.environ.get('IMGUR_CLIENT_ID')
    r = requests.delete('https://api.imgur.com/3/image/'+deletehash,
    headers={
        'Authorization': 'Client-ID ' + imgurClientID,
    })
    return r.json()
