
from flask import Flask,render_template,request
import pandas as  pd
import cv2
import base64
from pymongo import MongoClient
import joblib
import numpy as np

app=Flask(__name__)
app.static_folder='static'
model=joblib.load(open('model.pkl','rb'))
client = MongoClient("mongodb://127.0.0.1:27017")  # host uri
db = client.corona  # Select the database
corona_collection = db.corona  # Select the collection name
initial_tasks = [task for task in corona_collection.find()]


@app.route('/')
def home():
    return render_template("home.html")




@app.route('/form', methods=['POST','GET'])
def form():
    return render_template("form.html")


@app.route('/results',methods=['POST'])
def results():
    if request.method=='POST':
        try:
            name=str(request.form['name'])
            age=int(request.form['age'])
            sex=str(request.form['sex'])
            filestr = request.files['check'].read()
            npimg = np.fromstring(filestr, np.uint8)
            im=cv2.imdecode(npimg,cv2.IMREAD_GRAYSCALE)
            im=cv2.resize(im,(178,178))
            img=np.array(im)/.255
            img=np.reshape(img,(1,31684))
            pred= model.predict(img)       
            if (pred==1):
                msg='Immediately Reffer to nearest Doctor'
            else:
                msg='You seem to be safe ! Take all the precautions.'
            print(pred)
            db_ins={"name":name,"age":age,"sex":sex,"status":msg}
            #corona_collection.insert_one(db_ins)
            print('inserted')

        except:
            raise ValueError
            

    return render_template('results.html', msg='{}'.format(msg),name='{}'.format(name),age='{}'.format(age),sex='{}'.format(sex))


if __name__ == "__main__":
    app.run(debug=True)