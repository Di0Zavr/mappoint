from flask import Flask, render_template, request, Response
import db
from flask_mongoengine import MongoEngine
import json

app = Flask('__name__')
app.config['MONGODB_SETTINGS'] = {
    'db': 'map',
    'host': 'localhost',
    'port': 27017,
}
app_db = MongoEngine(app)


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/remove_fav', methods=['DELETE'])
def remove_favourite():
    try:
        user_id = request.form['user_id']
        point_id = request.form['point_id']
        point = db.PointOfInterest.objects(id=point_id)
        user = db.User.objects(id=user_id)
        if len(point) != 1 or len(user) != 1:
            return Response(status=422)

        fav = db.Favourite.objects(point=point[0], user=user[0])
        if len(fav) != 0:
            fav.delete()
            return Response(status=200)
        else:
            return Response(status=204)
    except:
        return Response(status=400)


@app.route('/api/add_fav', methods=['POST'])
def add_favourite():
    try:
        user_id = request.form['user_id']
        point_id = request.form['point_id']
        point = db.PointOfInterest.objects(id=point_id)
        user = db.User.objects(id=user_id)
        if len(point) != 1 or len(user) != 1:
            return Response(status=422)

        fav = db.Favourite(point=point[0], user=user[0])
        if len(db.Favourite.objects(point=point[0], user=user[0])) != 1:
            fav.save()

        return json.dumps(json.loads(db.Favourite.objects(point=point[0], user=user[0]).to_json()), ensure_ascii=False, indent=4)
    except:
        return Response(status=400)


@app.route('/api/town')
def town():
    return json.dumps(json.loads(db.Town.objects.order_by('name').to_json()), ensure_ascii=False, indent=4)


@app.route('/api/poi')
def poi():
    return json.dumps(json.loads(db.PointOfInterest.objects().order_by('title').to_json()), ensure_ascii=False, indent=4)


@app.route('/api/local_poi')
def local_poi():
    try:  # проверка что хэдер есть
        this_town = db.Town.objects(id=request.args['t'])
        if len(this_town) != 1:  # проверка, что с городом всё норм
            return Response(status=422)

        points = []
        local_points = db.PointOfInterest.objects(town=this_town[0])

        user = db.User.objects(id=request.form['user_id'])
        if len(user) != 0:
            fav_point_id = [point.point.id for point in db.Favourite.objects(user=user[0].id, point__in=local_points)]
            favourite_points = db.PointOfInterest.objects(town=this_town[0], id__in=fav_point_id).exclude('town')
            if len(favourite_points) != 0:
                fav_dict = {'tag': 'Избранное', 'points': json.loads(favourite_points.to_json())}
                points.append(fav_dict)

        for tag in db.Tag.objects:  # по тегам
            tag_point_id = [point.point.id for point in db.PointTag.objects(tag=tag, point__in=local_points)]
            tag_points = db.PointOfInterest.objects(town=this_town[0], id__in=tag_point_id).exclude('town')
            if len(tag_points) != 0:
                tag_dict = {'tag': tag.name, 'points': json.loads(tag_points.to_json())}
                points.append(tag_dict)
        json_response = {'town': json.loads(this_town[0].to_json()), 'town_points': points}

        return json.dumps(json_response, ensure_ascii=False, indent=4)
    except:
        return Response(status=500)


if __name__ == '__main__':
    app.run(debug=True)
