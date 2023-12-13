
from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api 
from models import restoran as restoranModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session

session = Session(engine)

app = Flask(__name__)
api = Api(app)        

class BaseMethod():

    def __init__(self):
        self.raw_weight = {'harga': 7, 'kualitas_pelayanan': 4, 'rating_makanan': 5, 'suasana': 6, 'lokasi': 4}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(restoranModel.id_restoran, restoranModel.harga, restoranModel.kualitas_pelayanan, restoranModel.rating_makanan, restoranModel.suasana, restoranModel.lokasi)
        result = session.execute(query).fetchall()
        print(result)
        return [{'id_restoran': restoran.id_restoran, 'harga': restoran.harga, 'kualitas_pelayanan': restoran.kualitas_pelayanan, 'rating_makanan': restoran.rating_makanan, 'suasana': restoran.suasana, 'lokasi': restoran.lokasi} for restoran in result]

    @property
    def normalized_data(self):
        harga_values = []
        kualitas_pelayanan_values = []
        rating_makanan_values = []
        suasana_values = []
        lokasi_values = []

        for data in self.data:
            harga_values.append(data['harga'])
            kualitas_pelayanan_values.append(data['kualitas_pelayanan'])
            rating_makanan_values.append(data['rating_makanan'])
            suasana_values.append(data['suasana'])
            lokasi_values.append(data['lokasi'])

        return [
            {'id_restoran': data['id_restoran'],
             'harga': min(harga_values) / data['harga'],
             'kualitas_pelayanan': data['kualitas_pelayanan'] / max(kualitas_pelayanan_values),
             'rating_makanan': data['rating_makanan'] / max(rating_makanan_values),
             'suasana': data['suasana'] / max(suasana_values),
             'lokasi': data['lokasi'] / max(lokasi_values)
             }
            for data in self.data
        ]

    def update_weights(self, new_weights):
        self.raw_weight = new_weights

class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = []

        for row in normalized_data:
            product_score = (
                row['harga'] ** self.raw_weight['harga'] *
                row['kualitas_pelayanan'] ** self.raw_weight['kualitas_pelayanan'] *
                row['rating_makanan'] ** self.raw_weight['rating_makanan'] *
                row['suasana'] ** self.raw_weight['suasana'] *
                row['lokasi'] ** self.raw_weight['lokasi']
            )

            produk.append({
                'id_restoran': row['id_restoran'],
                'produk': product_score
            })

        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)

        sorted_data = []

        for product in sorted_produk:
            sorted_data.append({
                'id_restoran': product['id_restoran'],
                'score': product['produk']
            })

        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return result, HTTPStatus.OK.value
    
    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'data': result}, HTTPStatus.OK.value
    

class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = {row['id_restoran']:
                  round(row['harga'] * weight['harga'] +
                        row['kualitas_pelayanan'] * weight['kualitas_pelayanan'] +
                        row['rating_makanan'] * weight['rating_makanan'] +
                        row['suasana'] * weight['suasana'] +
                        row['lokasi'] * weight['lokasi'], 2)
                  for row in self.normalized_data
                  }
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1], reverse=True))
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights

class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return result, HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'data': result}, HTTPStatus.OK.value


class restoran(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None
        
        if page > page_count or page < 1:
            abort(404, description=f'Halaman {page} tidak ditemukan.') 
        return {
            'page': page, 
            'page_size': page_size,
            'next': next_page, 
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = select(restoranModel)
        data = [{'id_restoran': restoran.id_restoran, 'rating_makanan': restoran.rating_makanan, 'harga': restoran.harga, 'kualitas_pelayanan': restoran.kualitas_pelayanan, 'suasana': restoran.suasana, 'lokasi': restoran.lokasi} for restoran in session.scalars(query)]
        return self.get_paginated_result('restoran/', data, request.args), HTTPStatus.OK.value


api.add_resource(restoran, '/restoran')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)
