# notes:
#
# set cloud platform:
# gcloud config set project gcp-hackathon2023-15
# make sure you are in hackathon folder (cd hackathon)
# to update changes:
# gcloud builds submit --tag us-central1-docker.pkg.dev/gcp-hackathon2023-15/kalani/hello-world
# to run and deploy:
# gcloud run deploy hello-world-2 --region us-central1 --image us-central1-docker.pkg.dev/gcp-hackathon2023-15/kalani/hello-world
#
# ask jeff if you need help: jwink@google.com

from google.cloud import bigquery
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask import Flask, render_template, send_from_directory, url_for, session
from datetime import datetime
import re
import os
import uuid
import base64


from google.cloud import aiplatform

from google.cloud.aiplatform.gapic.schema import predict


def predict_image_classification_sample(

    project: str,

    endpoint_id: str,

    file_content,

    location: str = "us-central1",

    api_endpoint: str = "us-central1-aiplatform.googleapis.com",

):

    # The AI Platform services require regional API endpoints.

    client_options = {"api_endpoint": api_endpoint}

    # Initialize client that will be used to create and send requests.

    # This client only needs to be created once, and can be reused for multiple requests.

    client = aiplatform.gapic.PredictionServiceClient(
        client_options=client_options)

    # with open(filename, "rb") as f:

    #     file_content = f.read()

    # The format of each instance should conform to the deployed model's prediction input schema.

    encoded_content = base64.b64encode(file_content).decode("utf-8")

    instance = predict.instance.ImageClassificationPredictionInstance(

        content=encoded_content,

    ).to_value()

    instances = [instance]

    # See gs://google-cloud-aiplatform/schema/predict/params/image_classification_1.0.0.yaml for the format of the parameters.

    parameters = predict.params.ImageClassificationPredictionParams(

        confidence_threshold=0.5, max_predictions=5,

    ).to_value()

    endpoint = client.endpoint_path(

        project=project, location=location, endpoint=endpoint_id

    )

    response = client.predict(

        endpoint=endpoint, instances=instances, parameters=parameters

    )

    print("response")

    print(" deployed_model_id:", response.deployed_model_id)

    # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.

    predictions = response.predictions

    for prediction in predictions:

        return round(dict(prediction)["confidences"][0])


def stream_data(self, table, data, schema):
    # first checks if table already exists. If it doesn't, then create it
    r = self.service.tables().list(projectId="gcp-hackathon2023-15",
                                   datasetId="gcp-hackathon2023-15.Package_View").execute()
    table_exists = [row['tableReference']['tableId'] for row in
                    r['tables'] if
                    row['tableReference']['tableId'] == table]
    if not table_exists:
        body = {
            'tableReference': {
                'tableId': table,
                'projectId': "gcp-hackathon2023-15",
                'datasetId': "gcp-hackathon2023-15.Package_View"
            },
            'schema': schema
        }
        self.service.tables().insert(projectId="gcp-hackathon2023-15",
                                     datasetId="gcp-hackathon2023-15.Package_View",
                                     body=body).execute()

    # with table created, now we can stream the data
    # to do so we'll use the tabledata().insertall() function.
    body = {
        'rows': [
            {
                'json': data,
                'insertId': str(uuid.uuid4())
            }
        ]
    }
    self.service.tabledata().insertAll(projectId="gcp-hackathon2023-15",
                                       datasetId="gcp-hackathon2023-15.Package_View",
                                       tableId=table,
                                       body=body).execute(num_retries=5)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldfkjlj'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, 'Only images are allows'),
            FileRequired('File field should not be empty')
        ]
    )
    submit = SubmitField('Upload')


@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


@app.route("/link/")
def link():
    #stream_data(self, table="gcp-hackathon2023-15.Package_View.PushTester", data = '[{"Tracking Number": "201929440", "Damaged": '+session.get("airesult", None)+' }]', schema = '[{"name": "Tracking Number", "mode": "NULLABLE", "type": "STRING", "description": null, "fields": []}, {"name": "Damaged", "mode": "NULLABLE", "type": "INTEGER", "description": null, "fields": [] }]')
    # Construct a BigQuery client object.
    client = bigquery.Client()
    # TODO(developer): Set table_id to the ID of table to append to.
    table_id = "gcp-hackathon2023-15.Package_View.PushTester"
    rows_to_insert = [
        {"Tracking Number": "201929440", "Damaged": session.get("airesult", None) }
    ]
    # Make an API request.
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))
    return render_template('success.html')
        


@app.route("/", methods=['GET', 'POST'])
def upload_image():
    form = UploadForm()
    if form.validate_on_submit():
        airesult = predict_image_classification_sample(
            project="366252188582",
            endpoint_id="6561388415311413248",
            location="us-central1",
            file_content=form.photo.data.read()
        )
        filename = photos.save(form.photo.data)
        file_url = url_for('get_file', filename=filename)
    else:
        file_url = None
        airesult = None
    session["airesult"] = airesult
    return render_template('index.html', form=form, file_url=file_url, airesult=airesult)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
