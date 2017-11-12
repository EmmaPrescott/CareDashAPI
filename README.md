# RestfulAPI

I created a RESTful API in python using flask, sqlalchemy (flask_sqlalchemy) and marshmallow (flask_marshmallow and marshmallow). I used an sqlite database. 

Install:

pip install -r requirements.txt

Run:

python app.py

and then run the bash/python script.


Comments on Design & Scalability:
  I created two models, Doctor and Review. In the review model, doctor_id is a foreign key to doctor.id, in order to know the doctor related to this review and vice versa. I created to Schemas for the models to store the relevant data in the database and had nested schemas for the reviews and doctor fields, in order to represent the foreign key relationship between objects. Currenty, potential scalability issues could be avoided by implementing a better and more complex database design, my design was simple for the purpose of this assignment and data is not deleted unless you explicitly delete it. Additionally, there is a possibility of redundant doctors, this could be solved by addingmore data fields for the doctor model to test if a doctor we want to add is already in the database or not.  
