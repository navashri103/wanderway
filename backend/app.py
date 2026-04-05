from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
import bcrypt
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'wanderway-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['wanderway']

users_col        = db['users']
destinations_col = db['destinations']
hotels_col       = db['hotels']
cabs_col         = db['cabs']
combos_col       = db['combos']
bookings_col     = db['bookings']


def fix_id(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def fix_ids(docs):
    return [fix_id(d) for d in docs]


def seed_data():
    if not users_col.find_one({'email': 'admin@wanderway.com'}):
        hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt())
        users_col.insert_one({'name': 'Admin', 'email': 'admin@wanderway.com', 'phone': '9999999999', 'password': hashed, 'role': 'admin'})
        print('Admin created')

    if destinations_col.count_documents({}) == 0:
        destinations_col.insert_many([
            {
                'name': 'Goa', 'category': 'Beach', 'state': 'Goa',
                'description': "India's smallest state packed with sun, sea, sand, and a laid-back vibe unlike anywhere else in the country.",
                'best_time': 'November to February', 'duration': '3-5 days', 'price': 8999,
                'image': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&q=80',
                'places_to_visit': [
                    {'name': 'Baga Beach', 'type': 'Beach', 'description': 'Most popular beach with water sports, shacks and nightlife.', 'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80'},
                    {'name': 'Basilica of Bom Jesus', 'type': 'Heritage', 'description': 'UNESCO Heritage Site housing the mortal remains of St. Francis Xavier.', 'image': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80'},
                    {'name': 'Dudhsagar Falls', 'type': 'Nature', 'description': 'Majestic four-tiered waterfall on the Goa-Karnataka border.', 'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=600&q=80'},
                    {'name': 'Fort Aguada', 'type': 'Heritage', 'description': '17th-century Portuguese fort with panoramic views of the Arabian Sea.', 'image': 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=600&q=80'},
                    {'name': 'Calangute Beach', 'type': 'Beach', 'description': 'Queen of Beaches — the longest and busiest beach in North Goa.', 'image': 'https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?w=600&q=80'}
                ]
            },
            {
                'name': 'Manali', 'category': 'Mountain', 'state': 'Himachal Pradesh',
                'description': 'A high-altitude Himalayan resort known for adventure, snow, river rafting and ancient temples.',
                'best_time': 'October to June', 'duration': '4-6 days', 'price': 12499,
                'image': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800&q=80',
                'places_to_visit': [
                    {'name': 'Rohtang Pass', 'type': 'Adventure', 'description': 'Snow-covered mountain pass at 3,978m with stunning views.', 'image': 'https://images.unsplash.com/photo-1598091383021-15ddea10925d?w=600&q=80'},
                    {'name': 'Solang Valley', 'type': 'Adventure', 'description': 'Famous for skiing, zorbing and paragliding with glacier backdrops.', 'image': 'https://images.unsplash.com/photo-1605540436563-5bca919ae766?w=600&q=80'},
                    {'name': 'Hadimba Temple', 'type': 'Religious', 'description': 'Ancient cave temple of Goddess Hadimba in a cedar forest.', 'image': 'https://images.unsplash.com/photo-1617859047452-8510bcf207fd?w=600&q=80'},
                    {'name': 'Beas River Rafting', 'type': 'Adventure', 'description': 'River rafting and trout fishing in scenic mountain valleys.', 'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80'},
                    {'name': 'Mall Road', 'type': 'Shopping', 'description': 'Main market for Kullu shawls, local handicrafts and street food.', 'image': 'https://images.unsplash.com/photo-1585246783459-69f9d1db6c82?w=600&q=80'}
                ]
            },
            {
                'name': 'Rajasthan', 'category': 'Heritage', 'state': 'Rajasthan',
                'description': 'The Land of Kings — golden deserts, ornate palaces, magnificent forts and colorful bazaars.',
                'best_time': 'October to March', 'duration': '6-8 days', 'price': 10299,
                'image': 'https://images.unsplash.com/photo-1477587458883-47145ed6736c?w=800&q=80',
                'places_to_visit': [
                    {'name': 'Amber Fort, Jaipur', 'type': 'Heritage', 'description': 'Hilltop fort of pale yellow and pink sandstone with stunning mirror work.', 'image': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&q=80'},
                    {'name': 'Lake Pichola, Udaipur', 'type': 'Nature', 'description': 'Artificial lake with island palaces and boat rides at sunset.', 'image': 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=600&q=80'},
                    {'name': 'Mehrangarh Fort, Jodhpur', 'type': 'Heritage', 'description': "One of India's largest forts perched 400 ft above the Blue City.", 'image': 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=600&q=80'},
                    {'name': 'Sam Sand Dunes', 'type': 'Adventure', 'description': 'Camel safari and overnight camping on Thar Desert dunes.', 'image': 'https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=600&q=80'},
                    {'name': 'Hawa Mahal', 'type': 'Heritage', 'description': 'Palace of Winds — five-storey pink sandstone with 953 windows.', 'image': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=600&q=80'}
                ]
            },
            {
                'name': 'Kerala', 'category': 'Nature', 'state': 'Kerala',
                'description': "God's Own Country — tropical paradise of backwaters, hill stations, wildlife and Ayurveda.",
                'best_time': 'September to March', 'duration': '4-6 days', 'price': 9799,
                'image': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80',
                'places_to_visit': [
                    {'name': 'Alleppey Backwaters', 'type': 'Nature', 'description': 'Houseboat cruise through canals, lakes and lagoons.', 'image': 'https://images.unsplash.com/photo-1593693411515-c20261bcad6e?w=600&q=80'},
                    {'name': 'Munnar Tea Gardens', 'type': 'Nature', 'description': 'Rolling hills of emerald green tea plantations at 1,600m.', 'image': 'https://images.unsplash.com/photo-1571401835393-8c5f35328320?w=600&q=80'},
                    {'name': 'Periyar Wildlife Sanctuary', 'type': 'Wildlife', 'description': 'Boat safari spotting wild elephants, bison and rare birds.', 'image': 'https://images.unsplash.com/photo-1549366021-9f761d450615?w=600&q=80'},
                    {'name': 'Varkala Beach', 'type': 'Beach', 'description': 'Dramatic cliff-backed beach with mineral springs and yoga retreats.', 'image': 'https://images.unsplash.com/photo-1583395838144-2b9a29f7d56c?w=600&q=80'},
                    {'name': 'Fort Kochi', 'type': 'Heritage', 'description': 'Colonial town with Chinese fishing nets and Jewish synagogue.', 'image': 'https://images.unsplash.com/photo-1617040619297-63f67a4fce3e?w=600&q=80'}
                ]
            },
            {
                'name': 'Leh Ladakh', 'category': 'Adventure', 'state': 'Ladakh',
                'description': 'High-altitude cold desert of dramatic mountains, crystal lakes and ancient monasteries.',
                'best_time': 'June to September', 'duration': '6-8 days', 'price': 18999,
                'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
                'places_to_visit': [
                    {'name': 'Pangong Lake', 'type': 'Nature', 'description': 'High-altitude lake at 4,350m that changes colour from blue to green.', 'image': 'https://images.unsplash.com/photo-1598163831958-83ab6f4e54c2?w=600&q=80'},
                    {'name': 'Nubra Valley', 'type': 'Nature', 'description': 'Double-humped Bactrian camels on sand dunes with snow peaks.', 'image': 'https://images.unsplash.com/photo-1605776583733-1ebf83e7d4f0?w=600&q=80'},
                    {'name': 'Thiksey Monastery', 'type': 'Religious', 'description': '12-storey gompa resembling the Potala Palace in Lhasa.', 'image': 'https://images.unsplash.com/photo-1604608672516-5f8ab1be4e63?w=600&q=80'},
                    {'name': 'Khardung La Pass', 'type': 'Adventure', 'description': "One of the world's highest motorable roads at 5,359m.", 'image': 'https://images.unsplash.com/photo-1621996659490-3275b4d0d951?w=600&q=80'},
                    {'name': 'Leh Palace', 'type': 'Heritage', 'description': 'Nine-storey ruins of the 17th-century royal palace.', 'image': 'https://images.unsplash.com/photo-1617859047452-8510bcf207fd?w=600&q=80'}
                ]
            },
            {
                'name': 'Andaman Islands', 'category': 'Beach', 'state': 'Andaman & Nicobar',
                'description': 'Remote islands with pristine coral reefs, turquoise water and powdery white sand beaches.',
                'best_time': 'October to May', 'duration': '5-7 days', 'price': 22999,
                'image': 'https://images.unsplash.com/photo-1586375300773-8384e3e4916f?w=800&q=80',
                'places_to_visit': [
                    {'name': 'Radhanagar Beach', 'type': 'Beach', 'description': "Asia's best beach — 2km of blinding white sand and crystal water.", 'image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80'},
                    {'name': 'Cellular Jail', 'type': 'Heritage', 'description': 'Colonial prison used by British — now a national memorial.', 'image': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80'},
                    {'name': 'North Bay Island', 'type': 'Adventure', 'description': 'Glass-bottom boats and scuba diving over living coral reefs.', 'image': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600&q=80'},
                    {'name': 'Neil Island', 'type': 'Nature', 'description': 'Quiet island with natural rock formations and snorkelling.', 'image': 'https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?w=600&q=80'},
                    {'name': 'Baratang Island', 'type': 'Nature', 'description': 'Limestone caves and mud volcanoes through mangrove creeks.', 'image': 'https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?w=600&q=80'}
                ]
            }
        ])
        print('Destinations seeded')

    if hotels_col.count_documents({}) == 0:
        hotels_col.insert_many([
            {'name': 'Ocean Breeze Resort', 'location': 'Goa', 'stars': 4, 'description': 'Beachfront resort with pool, spa and sea-view rooms.', 'price_per_night': 4500, 'image': 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=600&q=80'},
            {'name': 'Himalayan Retreat', 'location': 'Manali', 'stars': 3, 'description': 'Cozy mountain lodge with bonfire evenings and valley views.', 'price_per_night': 2800, 'image': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600&q=80'},
            {'name': 'Palace Heritage Hotel', 'location': 'Jaipur', 'stars': 5, 'description': 'Restored palace with royal dining and elephant rides.', 'price_per_night': 8999, 'image': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&q=80'},
            {'name': 'Backwater Houseboat', 'location': 'Kerala', 'stars': 4, 'description': 'Traditional houseboat drifting Alleppey backwaters with all meals.', 'price_per_night': 6200, 'image': 'https://images.unsplash.com/photo-1593693411515-c20261bcad6e?w=600&q=80'},
            {'name': 'The Leh Lodge', 'location': 'Leh', 'stars': 3, 'description': 'Warm high-altitude stay with mountain views and local cuisine.', 'price_per_night': 3200, 'image': 'https://images.unsplash.com/photo-1526786220381-1d21eedf72bf?w=600&q=80'},
        ])
        print('Hotels seeded')

    if cabs_col.count_documents({}) == 0:
        cabs_col.insert_many([
            {'name': 'Swift Dzire', 'type': 'Cab', 'seats': 4, 'description': 'Comfortable AC sedan for city and outstation trips.', 'price_per_km': 12, 'image': 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600&q=80'},
            {'name': 'Innova Crysta', 'type': 'SUV', 'seats': 7, 'description': 'Spacious 7-seater AC SUV for family trips and mountain roads.', 'price_per_km': 18, 'image': 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=600&q=80'},
            {'name': 'Royal Enfield', 'type': 'Bike', 'seats': 2, 'description': 'Iconic bike for mountain passes, coastal roads and adventure routes.', 'price_per_km': 5, 'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80'},
            {'name': 'Electric Auto', 'type': 'Auto', 'seats': 3, 'description': 'Eco-friendly electric auto for short local trips.', 'price_per_km': 8, 'image': 'https://images.unsplash.com/photo-1612831197820-f9f0a0b3eb64?w=600&q=80'},
            {'name': 'Mercedes E-Class', 'type': 'Luxury', 'seats': 4, 'description': 'Premium luxury cab with uniformed chauffeur service.', 'price_per_km': 35, 'image': 'https://images.unsplash.com/photo-1617531653332-bd46c16f7d79?w=600&q=80'},
        ])
        print('Cabs seeded')

    if combos_col.count_documents({}) == 0:
        combos_col.insert_many([
            {'name': 'Goa Bliss Pack', 'destination': 'Goa', 'duration': 4, 'total_price': 18999, 'image': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=600&q=80', 'includes': ['3 nights Ocean Breeze Resort', 'Return flights from Chennai', 'Airport cab both ways', 'Daily breakfast', 'Beach water sports pass']},
            {'name': 'Manali Snow Adventure', 'destination': 'Manali', 'duration': 5, 'total_price': 24999, 'image': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=600&q=80', 'includes': ['4 nights Himalayan Retreat', 'Volvo bus tickets', 'SUV sightseeing Rohtang & Solang', 'All meals', 'Snow activity package']},
            {'name': 'Rajasthan Royal Tour', 'destination': 'Rajasthan', 'duration': 7, 'total_price': 32999, 'image': 'https://images.unsplash.com/photo-1477587458883-47145ed6736c?w=600&q=80', 'includes': ['6 nights Jaipur + Jodhpur + Udaipur', 'AC cab across cities', 'Guided fort tours', 'Breakfast + Dinner', 'Camel safari Jaisalmer']},
            {'name': 'Kerala Backwaters Escape', 'destination': 'Kerala', 'duration': 4, 'total_price': 21999, 'image': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&q=80', 'includes': ['2 nights Munnar resort', '1 night houseboat', 'All transfers by AC cab', 'All meals on houseboat', 'Kathakali show entry']},
        ])
        print('Combos seeded')

    print('Database ready.')


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Name, email and password required'}), 400
    if users_col.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 400
    hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
    users_col.insert_one({'name': data['name'], 'email': data['email'], 'phone': data.get('phone',''), 'password': hashed, 'role': 'user'})
    return jsonify({'message': 'Account created'}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user = users_col.find_one({'email': data.get('email')})
    if not user or not bcrypt.checkpw(data.get('password','').encode(), user['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    token = create_access_token(identity=str(user['_id']))
    return jsonify({'token': token, 'user': {'id': str(user['_id']), 'name': user['name'], 'email': user['email'], 'role': user['role']}})


@app.route('/destinations', methods=['GET'])
def get_destinations():
    q = request.args.get('q','')
    query = {'$or': [{'name':{'$regex':q,'$options':'i'}},{'category':{'$regex':q,'$options':'i'}},{'state':{'$regex':q,'$options':'i'}},{'description':{'$regex':q,'$options':'i'}}]} if q else {}
    return jsonify(fix_ids(list(destinations_col.find(query))))


@app.route('/destinations/<dest_id>', methods=['GET'])
def get_destination(dest_id):
    d = destinations_col.find_one({'_id': ObjectId(dest_id)})
    if not d: return jsonify({'error': 'Not found'}), 404
    return jsonify(fix_id(d))


@app.route('/hotels', methods=['GET'])
def get_hotels():
    q = request.args.get('q','')
    query = {'$or': [{'name':{'$regex':q,'$options':'i'}},{'location':{'$regex':q,'$options':'i'}}]} if q else {}
    return jsonify(fix_ids(list(hotels_col.find(query))))


@app.route('/cabs', methods=['GET'])
def get_cabs():
    q = request.args.get('q','')
    query = {'$or': [{'name':{'$regex':q,'$options':'i'}},{'type':{'$regex':q,'$options':'i'}}]} if q else {}
    return jsonify(fix_ids(list(cabs_col.find(query))))


@app.route('/combos', methods=['GET'])
def get_combos():
    return jsonify(fix_ids(list(combos_col.find({}))))


@app.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    user = users_col.find_one({'_id': ObjectId(user_id)})
    data = request.json
    bookings_col.insert_one({'user_id': user_id, 'user_name': user['name'] if user else 'Unknown', 'user_email': user['email'] if user else '', 'type': data['type'], 'item_id': data['item_id'], 'item_name': data['item_name'], 'date': data['date'], 'qty': data['qty'], 'notes': data.get('notes',''), 'total_price': data['total_price'], 'status': 'confirmed'})
    return jsonify({'message': 'Booking confirmed!'}), 201


@app.route('/bookings/mine', methods=['GET'])
@jwt_required()
def my_bookings():
    user_id = get_jwt_identity()
    return jsonify(fix_ids(list(bookings_col.find({'user_id': user_id}).sort('_id',-1))))


@app.route('/bookings/<booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    result = bookings_col.update_one({'_id': ObjectId(booking_id), 'user_id': user_id}, {'$set': {'status': 'cancelled'}})
    if result.modified_count == 0: return jsonify({'error': 'Not found'}), 404
    return jsonify({'message': 'Cancelled'})


def require_admin():
    user_id = get_jwt_identity()
    user = users_col.find_one({'_id': ObjectId(user_id)})
    return user if user and user.get('role') == 'admin' else None


@app.route('/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    if not require_admin(): return jsonify({'error': 'Admin only'}), 403
    rev = list(bookings_col.aggregate([{'$match':{'status':'confirmed'}},{'$group':{'_id':None,'total':{'$sum':'$total_price'}}}]))
    return jsonify({'users': users_col.count_documents({}), 'bookings': bookings_col.count_documents({}), 'revenue': rev[0]['total'] if rev else 0, 'destinations': destinations_col.count_documents({})})


@app.route('/admin/bookings', methods=['GET'])
@jwt_required()
def admin_bookings():
    if not require_admin(): return jsonify({'error': 'Admin only'}), 403
    return jsonify(fix_ids(list(bookings_col.find({}).sort('_id',-1).limit(100))))


@app.route('/admin/users', methods=['GET'])
@jwt_required()
def admin_users():
    if not require_admin(): return jsonify({'error': 'Admin only'}), 403
    return jsonify(fix_ids(list(users_col.find({}, {'password': 0}))))


@app.route('/admin/destinations', methods=['POST'])
@jwt_required()
def admin_add_destination():
    if not require_admin(): return jsonify({'error': 'Admin only'}), 403
    destinations_col.insert_one(request.json)
    return jsonify({'message': 'Added'}), 201


@app.route('/admin/hotels', methods=['POST'])
@jwt_required()
def admin_add_hotel():
    if not require_admin(): return jsonify({'error': 'Admin only'}), 403
    hotels_col.insert_one(request.json)
    return jsonify({'message': 'Added'}), 201


@app.route('/admin/cabs', methods=['POST'])
@jwt_required()
def admin_add_cab():
    if not require_admin(): return jsonify({'error': 'Admin only'}), 403
    cabs_col.insert_one(request.json)
    return jsonify({'message': 'Added'}), 201


@app.route('/admin/combos', methods=['POST'])
@jwt_required()
def admin_add_combo():
    if not require_admin(): return jsonify({'error': 'Admin only'}), 403
    combos_col.insert_one(request.json)
    return jsonify({'message': 'Added'}), 201


# ── DB VIEWER for review/presentation ──
@app.route('/admin/db-viewer', methods=['GET'])
@jwt_required()
def db_viewer():
    if not require_admin(): return jsonify({'error': 'Admin only'}), 403
    return jsonify({
        'users':        fix_ids(list(users_col.find({}, {'password': 0}))),
        'destinations': fix_ids(list(destinations_col.find({}, {'places_to_visit': 0}))),
        'hotels':       fix_ids(list(hotels_col.find({}))),
        'cabs':         fix_ids(list(cabs_col.find({}))),
        'combos':       fix_ids(list(combos_col.find({}))),
        'bookings':     fix_ids(list(bookings_col.find({}).sort('_id',-1).limit(50)))
    })


if __name__ == '__main__':
    seed_data()
    print('\nWanderWay running at http://127.0.0.1:5000\n')
    app.run(debug=True)
