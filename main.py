from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import utils.json_utils as js

app=Flask(__name__)
USER_FILE="data/user.json"
PATIENT_FILE="data/patient.json"
SUMMARY_FILE="data/summary.json"
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
            session["msg"]=""
            login=True
    return login

def calc_summary():
    data=js.read_json(PATIENT_FILE)
    summary_data=js.read_json(SUMMARY_FILE)
    treatment_total=0
    lab_cost_total=0
    pat_bal_total=0
    lab_bal_total=0
    lab_paid_total=0
    pat_paid_total=0
    for pid,pdata in data.items():
        treatment_total=treatment_total+pdata["Total"]
        lab_cost_total=lab_cost_total+pdata["Lab_cost"]
        pat_bal_total=pat_bal_total+pdata["patient_balance"]
        lab_bal_total=lab_bal_total+pdata["Lab_balance"]
        lab_paid_total=lab_paid_total+pdata["Lab_paid"]
        pat_paid_total=pat_paid_total+pdata["Advance"]
    summary_data["Treatment_total"]=treatment_total
    summary_data["lab_cost_total"]=lab_cost_total
    summary_data["pat_bal_total"]=pat_bal_total
    summary_data["lab_bal_total"]=lab_bal_total
    summary_data["lab_paid_total"]=lab_paid_total
    summary_data["pat_paid_total"]=pat_paid_total
    js.writejson(summary_data,SUMMARY_FILE)
    return summary_data
        
@app.route("/home",methods=["POST","GET"])
def home_redirect():
    if checkauth():
        data=js.read_json(PATIENT_FILE)
        msg=session["msg"]
        session["msg"]=""
        return render_template("home.html",data=data,summary=calc_summary(),msg=msg)
    else:
        return redirect("/")
    

@app.route("/logout", methods=["POST","GET"])
def logout():
      print("logging out ...")
      for key in list(session.keys()):
            session.pop(key)
      return redirect("/")

@app.route("/update/<pid>", methods=["POST","GET"])
def update(pid):
    if checkauth():
        data=js.read_json(PATIENT_FILE)
        for pt in data.keys():
            if pt==pid:
                data[pid]["Name"]=request.form["name"]
                data[pid]["Contact"]=request.form["cnt"]
                data[pid]["Work"]=request.form["work"]
                data[pid]["Total"]=int(request.form["total"])
                data[pid]["patient_balance"]=data[pid]["Total"]-data[pid]["Advance"]
        js.writejson(data,PATIENT_FILE)
        return redirect("/home")
    else:
        return redirect("/")
            
    
@app.route("/add_pt", methods=["POST","GET"])
def add_pt():
    if checkauth():
        data=js.read_json(PATIENT_FILE)
        if request.method=="POST":
            pid=get_pid()
            if pid=="fail":
                session["msg"]="Error ! Unable to register... Please contact admin..."
                return redirect("/home")
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
        return redirect("/home")
    return redirect("/")
        
@app.route("/payment",methods=["POST","GET"])
def payment():
    if checkauth():
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
                session["msg"]="Unable to make paymet please contact admin"
            js.writejson(data,PATIENT_FILE)
        return redirect("/home")
    return redirect("/")

@app.route("/", methods=["POST","GET"])
def home():
    msg=""
    if request.method=="POST":
        if login(request.form["username"],request.form["password"]):
            return redirect("/home")
        else:
            msg="Invalid credentials"
    return render_template("login.html",msg=msg)



if __name__=="__main__":
    app.run(debug=True)

