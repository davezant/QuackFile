# QuackFile

A temporary, encrypted file-sharing server. It stores payloads for up to 180 seconds.

###### Most tools for quick sharing store metadata or human-readable content on the server disk. QuackFile intercepts data in memory, applies Fernet symmetric encryption, and writes only the ciphertext to storage. The decryption key stays exclusively in the server quick memory and vanishes forever once the file is downloaded or reaches the 180-second timeout.

### Features

- Maximum of 3 minutes to receive a file to avoid snoopers.

- Up to 50 MB per file.

- Quick access between devices.

- Responsive and beautiful design. Duck themed ;)

### Todo...

- Make better design overall with duck related thingies.

- Interactable donation box to [Heifer's flock of ducks](https://www.heifer.org/give/gift-catalog/animals/flock-of-ducks).
  
- Suggestions are welcome.
---

### Usage
Setup the website using:
```
pip install -r requirements.txt
python3 app.py
```
Adjust your settings like app.debug at app.py file, or constants at /lib/constants.py

---
### Core API Endpoints
#### Upload Payload
```
   
 URL: /send-payload

    Method: POST

    Payload: Multipart Form or JSON/Form Text (text).

    Observation: Maximum of 50Mb.    

    Response:

JSON

{
  "code": 200,
  "id": "GT5-1UN",
  "status": "success"
}
```
#### Download Payload

    URL: /receive/<code_id>

    Method: GET

    Behavior: Streams the decrypted data and instantly deletes the source file from disk and the key from memory.

### Early Cancellation

    URL: /cancel/<code_id>

    Method: DELETE / POST / GET

    Behavior: Purges the encrypted file from the filesystem immediately.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[Apache](http://www.apache.org/licenses/LICENSE-2.0)
