from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import utils.json_utils as js
from datetime import date,datetime

app=Flask(__name__)
USER_FILE="data/user.json"
PATIENT_FILE="data/patient.json"
SUMMARY_FILE="data/summary.json"
ARCH_FILE="data/archive.json"
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

@app.route("/cleararchive",methods=["POST","GET"])
def cleararchive():
    if checkauth():
        todays_date =datetime.strptime(str(date.today()),r"%Y-%m-%d")
        data=js.read_json(ARCH_FILE)
        for pt in data["archived"]:
            arch_date=datetime.strptime(pt["archivedate"],r"%Y-%m-%d")
            date_diff=str((todays_date-arch_date).days)
            if int(date_diff)>180:
                data["archived"].remove(pt)
        sno=1
        for pt in data["archived"]:
            pt["sno"]=sno
            sno+=1
        js.writejson(data,ARCH_FILE)
        return redirect("/viewarchive")
    else:
        return redirect("/")
    
    

@app.route("/logout", methods=["POST","GET"])
def logout():
      print("logging out ...")
      for key in list(session.keys()):
            session.pop(key)
      return redirect("/")

@app.route("/viewarchive",methods=["POST","GET"])
def vew_archive():
    if checkauth():
        arch_data=js.read_json(ARCH_FILE)
        return render_template("arch_data.html",arch_data=arch_data["archived"])
    else:
        return redirect("/")
  
@app.route("/archive_all", methods=["POST","GET"])
def archive_all():
    if checkauth():
        data=js.read_json(PATIENT_FILE)
        arch_data=js.read_json(ARCH_FILE)
        arch_list=[]
        todays_date = date.today()
        for pid in data.keys():
            if data[pid]["patient_balance"]==0 and data[pid]["Lab_balance"]==0:
                pt_data={
                    "sno": len(arch_data["archived"])+1,
                    "name":data[pid]["Name"],
                    "contact":data[pid]["Contact"],
                    "work":data[pid]["Work"],
                    "total":data[pid]["Total"],
                    "paid":data[pid]["Advance"],
                    "lab_total":data[pid]["Lab_cost"],
                    "lab_paid":data[pid]["Lab_paid"],
                    "patient_bal":data[pid]["patient_balance"],
                    "lab_bal":data[pid]["Lab_balance"],
                    "archivedate":str(todays_date),
                    "month":int(todays_date.month),
                    "year": int(todays_date.year)
                }
                arch_list.append(pid)
                arch_data["archived"].append(pt_data)
        for pid in arch_list:
            del data[pid]
        js.writejson(data,PATIENT_FILE)
        js.writejson(arch_data,ARCH_FILE)
        session["msg"]=f"archive done for {len(arch_list)} data"
        return redirect("/home")
    else:
        return redirect("/")
        
    
    

@app.route("/archive/<pid>", methods=["POST","GET"])
def archive(pid):
    if checkauth():
        data=js.read_json(PATIENT_FILE)
        arch_data=js.read_json(ARCH_FILE)
        todays_date = date.today()
        present=False
        for pt in data.keys():
            if pt==pid:
                present=True
                pt_data={
                    "sno": len(arch_data["archived"])+1,
                    "name":data[pid]["Name"],
                    "contact":data[pid]["Contact"],
                    "work":data[pid]["Work"],
                    "total":data[pid]["Total"],
                    "paid":data[pid]["Advance"],
                    "lab_total":data[pid]["Lab_cost"],
                    "lab_paid":data[pid]["Lab_paid"],
                    "patient_bal":data[pid]["patient_balance"],
                    "lab_bal":data[pid]["Lab_balance"],
                    "archivedate":str(todays_date),
                    "month":int(todays_date.month),
                    "year": int(todays_date.year)
                }
                arch_data["archived"].append(pt_data)
        if present:
            del data[pid]
        js.writejson(data,PATIENT_FILE)
        js.writejson(arch_data,ARCH_FILE)
        session["msg"]="Data archivied for " + pt_data["name"]
        return redirect("/home")
    else:
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
                data[pid]["Lab_cost"]=int(request.form["labcost"])
                data[pid]["Lab_balance"]=data[pid]["Lab_cost"]-data[pid]["Lab_paid"]
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
            try:
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
            except:
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

