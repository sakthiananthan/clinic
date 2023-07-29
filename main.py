from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import utils.json_utils as js

app=Flask(__name__)
USER_FILE="data/user.json"
PATIENT_FILE="data/patient.json"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_pid():
    data=js.read_json(PATIENT_FILE)
    key_len=len(data.keys())+1
    for i in range(key_len):
        if "p_00"+str(key_len) not in data.keys():
            return "p_00"+str(key_len)
        else:
            key_len+=1
    return "fail"

def checkauth():
    try:
        if session["name"]:
           return True
        else:
            return False
    except:
        return False
    
def login(username,password):
    user_data=js.read_json(USER_FILE)
    login=False
    for user in user_data["users"]:
        if user["username"]==username and user["password"]==password:
            session["name"]="sakthi"
            login=True
    return login

@app.route("/logout", methods=["POST","GET"])
def logout():
      print("logging out ...")
      for key in list(session.keys()):
            session.pop(key)
      return redirect("/")
  
@app.route("/add_pt", methods=["POST","GET"])
def add_pt():
    msg=""
    if checkauth():
        data=js.read_json(PATIENT_FILE)
        if request.method=="POST":
            pid=get_pid()
            if pid=="fail":
                msg="Error ! Unable to register... Please contact admin..."
                return render_template("home.html",msg=msg,data=data)
            if request.form["advance"]=="":
                advance=0
            else:
                advance=int(request.form["advance"])
            if request.form["lab_total"]=="":
                lab_cst=0
            else:
                lab_cst=int(request.form["lab_total"])
            data[pid]={
                "Name": request.form["name"],
                "Contact": request.form["cno"],
                "Work" : request.form["work"],
                "Total": int(request.form["total"]),
                "Advance": advance,
                "Lab_cost": lab_cst,
                "Lab_paid": 0,
                "patient_balance": int(request.form["total"])-advance,
                "Lab_balance": lab_cst
            }
            js.writejson(data,PATIENT_FILE)
        return render_template("home.html",data=data)
    return redirect("/")
        
@app.route("/payment",methods=["POST","GET"])
def payment():
    if checkauth():
        msg=""
        data=js.read_json(PATIENT_FILE)
        if request.method=="POST":
            pid=request.form["pid"]
            print(request.form["type"])
            if request.form["type"]=="Lab":
                data[pid]["Lab_paid"]=data[pid]["Lab_paid"]+int(request.form["amount"])
                data[pid]["Lab_balance"]=data[pid]["Lab_cost"]-data[pid]["Lab_paid"]
            elif request.form["type"]=="patient":
                data[pid]["Advance"]=data[pid]["Advance"]+int(request.form["amount"])
                data[pid]["patient_balance"]=data[pid]["Total"]-data[pid]["Advance"]
            else:
                msg="Unable to make paymet please contact admin"
            js.writejson(data,PATIENT_FILE)
        return render_template("home.html",data=data,msg=msg)
    return redirect("/")

@app.route("/", methods=["POST","GET"])
def home():
    msg=""
    if request.method=="POST":
        if login(request.form["username"],request.form["password"]):
            data=js.read_json(PATIENT_FILE)
            return render_template("home.html",data=data)
        else:
            msg="Invalid credentials"
    return render_template("login.html",msg=msg)



if __name__=="__main__":
    app.run(debug=True)

