const mongoose = require('mongoose');

const Schema = mongoose.Schema;

const lalkaSchema = new Schema({
    user_id: {
        type: Number,
        required: true
    },
    nickname: {
        name: String,
        max: Number,
        link: Boolean
    },
    money: {
        cash: Number,
        bank: Number,
        dollar: Number,
        bitcoin: Number
    },
    donate_balance: {
        type: Number,
        required: true
    },
    job: {
        title: String,
        level: Number,
        salary: Number,
        description: String,
        tasks_completed: Number,
        next_job: Date
    },
    job_lvl: Number,
    house: {
        houses: [{
            id: Number
        }],
        maxPlaces: Number,
        order: [{
            from_user: Number,
            to_user: Number,
            house_id: Number,
            price: Number,
            ucode: String
        }],
        offer: [{
            from_user: Number,
            to_user: Number,
            house_id: Number,
            price: Number,
            ucode: String
        }]
    },
    car: {
        cars: [{
            id: Number,
            name: String,
            price: Number,
            plate: String
        }],
        maxPlaces: Number,
        order: [{
            from_user: Number,
            to_user: Number,
            type_transport: String,
            transport_id: Number,
            price: Number,
            ucode: String
        }],
        offer: [{
            from_user: Number,
            to_user: Number,
            type_transport: String,
            transport_id: Number,
            price: Number,
            ucode: String
        }]
    },
    yacht: {
        yachts: [{
            id: Number,
            name: String,
            price: Number
        }],
        maxPlaces: Number,
        order: [{
            from_user: Number,
            to_user: Number,
            type_transport: String,
            transport_id: Number,
            price: Number,
            ucode: String
        }],
        offer: [{
            from_user: Number,
            to_user: Number,
            type_transport: String,
            transport_id: Number,
            price: Number,
            ucode: String
        }]
    },
    registration: Date,
    active: Boolean,
    language: String,
    username: String
})

const Lalka = mongoose.model('lerkalalka', lalkaSchema);

module.exports = Lalka;