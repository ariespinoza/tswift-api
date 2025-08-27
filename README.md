# TSwift API (Flask + Docker)

A simple API built with Flask and packaged with Docker. It serves **Taylor Swift albums** data that is consumed by the iOS SwiftUI app.

## Endpoints
- **GET** `/` → health check (returns "Hello, API is running!")  
- **GET** `/albums` → returns all albums with fields:  
  - `id`  
  - `name`  
  - `imageName` (array of asset names)  
  - `releaseDate`  
  - `trackList` (array of strings)  

### Example response
```json
{
  "count": 12,
  "items": [
    {
      "id": 1,
      "name": "Taylor Swift",
      "imageName": ["Debut"],
      "releaseDate": "October 24, 2006",
      "trackList": ["Tim McGraw", "Picture to Burn", "..."]
    }
  ]
}



