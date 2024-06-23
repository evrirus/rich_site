// const { MongoClient } = require('mongodb');

// async function connectToDatabase() {
//     const client = new MongoClient('mongodb://localhost:27017');

//     try {
//         await client.connect();
//         console.log('Connected to the database');

//         const database = client.db('lalka');
//         const collection = database.collection('lerkalalka');

//         // Выполнение запроса findOne
//         const result = await collection.findOne({ user_id: 899827113 });
        
//         if (result) {
//             console.log(result);
//         } else {
//             console.log("Данные не найдены");
//         }
//     } catch (err) {
//         console.error(err);
//     } finally {
//         await client.close();
//     }
// }

// connectToDatabase();


const express = require('express')
const app = express()
const PORT = 3000
const path = require('path');

const createPath = (page) => path.resolve(__dirname, 'views', `${page}.html`);

// console.log(path.resolve(__dirname, 'views', `${page}.html`));
app.use('', express.static(__dirname));

app.listen(PORT, (error) => {
    error ? console.log(error) : console.log(`Example app listening on port ${PORT}`);
});

app.get('/', (req, res) => {
    res.setHeader('content-type', 'text/html');
    res.sendFile(createPath('index'));
});

app.get('/profile', (req, res) => {
    res.setHeader('content-type', 'text/html');
    res.sendFile(createPath('profile'));

});

const handleError = (res, error) => {
    res.status(500).json({error});
} 

// app.get('/lera', (req, res) => {
    

// });
